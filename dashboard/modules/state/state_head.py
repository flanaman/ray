import logging

import aiohttp.web

import dataclasses

from typing import Callable

from ray.dashboard.datacenter import DataSource
from ray.dashboard.utils import Change
import ray.dashboard.utils as dashboard_utils
import ray.dashboard.optional_utils as dashboard_optional_utils
from ray.dashboard.optional_utils import rest_response
from ray.dashboard.modules.log.log_manager import (
    LogsManager,
)
from ray.dashboard.state_aggregator import StateAPIManager
from ray.experimental.state.common import (
    ListApiOptions,
    GetLogOptions,
    DEFAULT_RPC_TIMEOUT,
)
from ray.experimental.state.exception import DataSourceUnavailable
from ray.experimental.state.state_manager import StateDataSourceClient

logger = logging.getLogger(__name__)
routes = dashboard_optional_utils.ClassMethodRouteTable


class StateHead(dashboard_utils.DashboardHeadModule):
    """Module to obtain state information from the Ray cluster.

    It is responsible for state observability APIs such as
    ray.list_actors(), ray.get_actor(), ray.summary_actors().
    """

    def __init__(self, dashboard_head):
        super().__init__(dashboard_head)
        self._state_api_data_source_client = None
        self._state_api = None
        self._log_api = None
        DataSource.nodes.signal.append(self._update_raylet_stubs)
        DataSource.agents.signal.append(self._update_agent_stubs)

    def _options_from_req(self, req) -> ListApiOptions:
        """Obtain `ListApiOptions` from the aiohttp request."""
        limit = int(req.query.get("limit"))
        timeout = int(req.query.get("timeout"))
        filter_keys = req.query.getall("filter_keys", [])
        filter_values = req.query.getall("filter_values", [])
        assert len(filter_keys) == len(filter_values)
        filters = []
        for key, val in zip(filter_keys, filter_values):
            filters.append((key, val))
        return ListApiOptions(limit=limit, timeout=timeout, filters=filters)

    def _reply(self, success: bool, error_message: str, result: dict, **kwargs):
        """Reply to the client."""
        return rest_response(
            success=success,
            message=error_message,
            result=result,
            convert_google_style=False,
            **kwargs,
        )

    async def _update_raylet_stubs(self, change: Change):
        """Callback that's called when a new raylet is added to Datasource.

        Datasource is a api-server-specific module that's updated whenever
        api server adds/removes a new node.

        Args:
            change: The change object. Whenever a new node is added
                or removed, this callback is invoked.
                When new node is added: information is in `change.new`.
                When a node is removed: information is in `change.old`.
                When a node id is overwritten by a new node with the same node id:
                    `change.old` contains the old node info, and
                    `change.new` contains the new node info.
        """
        if change.old:
            # When a node is deleted from the DataSource or it is overwritten.
            node_id, node_info = change.old
            self._state_api_data_source_client.unregister_raylet_client(node_id)
        if change.new:
            # When a new node information is written to DataSource.
            node_id, node_info = change.new
            self._state_api_data_source_client.register_raylet_client(
                node_id,
                node_info["nodeManagerAddress"],
                int(node_info["nodeManagerPort"]),
            )

    async def _update_agent_stubs(self, change: Change):
        """Callback that's called when a new agent is added to Datasource."""
        if change.old:
            node_id, _ = change.old
            self._state_api_data_source_client.unregister_agent_client(node_id)
        if change.new:
            # When a new node information is written to DataSource.
            node_id, ports = change.new
            ip = DataSource.node_id_to_ip[node_id]
            self._state_api_data_source_client.register_agent_client(
                node_id,
                ip,
                int(ports[1]),
            )

    async def _handle_list_api(
        self, list_api_fn: Callable[[ListApiOptions], dict], req: aiohttp.web.Request
    ):
        try:
            result = await list_api_fn(option=self._options_from_req(req))
            return self._reply(
                success=True,
                error_message="",
                result=result.result,
                partial_failure_warning=result.partial_failure_warning,
            )
        except DataSourceUnavailable as e:
            return self._reply(success=False, error_message=str(e), result=None)

    @routes.get("/api/v0/actors")
    async def list_actors(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        return await self._handle_list_api(self._state_api.list_actors, req)

    @routes.get("/api/v0/jobs")
    async def list_jobs(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        try:
            result = self._state_api.list_jobs(option=self._options_from_req(req))
            return self._reply(
                success=True,
                error_message="",
                result={
                    job_id: dataclasses.asdict(job_info)
                    for job_id, job_info in result.result.items()
                },
                partial_failure_warning=result.partial_failure_warning,
            )
        except DataSourceUnavailable as e:
            return self._reply(success=False, error_message=str(e), result=None)

    @routes.get("/api/v0/nodes")
    async def list_nodes(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        return await self._handle_list_api(self._state_api.list_nodes, req)

    @routes.get("/api/v0/placement_groups")
    async def list_placement_groups(
        self, req: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        return await self._handle_list_api(self._state_api.list_placement_groups, req)

    @routes.get("/api/v0/workers")
    async def list_workers(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        return await self._handle_list_api(self._state_api.list_workers, req)

    @routes.get("/api/v0/tasks")
    async def list_tasks(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        return await self._handle_list_api(self._state_api.list_tasks, req)

    @routes.get("/api/v0/objects")
    async def list_objects(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        return await self._handle_list_api(self._state_api.list_objects, req)

    @routes.get("/api/v0/runtime_envs")
    async def list_runtime_envs(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        return await self._handle_list_api(self._state_api.list_runtime_envs, req)

    @routes.get("/api/v0/logs")
    async def list_logs(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        """Return a list of log files on a given node id.

        Unlike other list APIs that display all existing resources in the cluster,
        this API always require to specify node id and node ip.
        """
        glob_filter = req.query.get("glob", "*")
        node_id = req.query.get("node_id", None)
        node_ip = req.query.get("node_ip", None)
        timeout = req.query.get("timeout", DEFAULT_RPC_TIMEOUT)

        # TODO(sang): Do input validation from the middleware instead.
        if not node_id and not node_ip:
            return self._reply(
                success=False,
                error_message=(
                    "Both node id and node ip are not provided. "
                    "Please provide at least one of them."
                ),
                result=None,
            )

        node_id = node_id or self._log_api.ip_to_node_id(node_ip)
        if not node_id:
            return self._reply(
                success=False,
                error_message=(
                    f"Cannot find matching node_id for a given node ip {node_ip}"
                ),
                result=None,
            )

        try:
            result = await self._log_api.list_logs(
                node_id, timeout, glob_filter=glob_filter
            )
        except DataSourceUnavailable as e:
            return self._reply(success=False, error_message=str(e), result=None)

        return self._reply(success=True, error_message="", result=result)

    @routes.get("/api/v0/logs/{media_type}")
    async def get_logs(self, req: aiohttp.web.Request):
        """
        If `media_type = stream`, creates HTTP stream which is either kept alive while
        the HTTP connection is not closed. Else, if `media_type = file`, the stream
        ends once all the lines in the file requested are transmitted.
        """
        options = GetLogOptions(
            timeout=req.query.get("timeout", DEFAULT_RPC_TIMEOUT),
            node_id=req.query.get("node_id"),
            node_ip=req.query.get("node_ip"),
            media_type=req.match_info.get("media_type", "file"),
            filename=req.query.get("filename"),
            actor_id=req.query.get("actor_id"),
            task_id=req.query.get("task_id"),
            pid=req.query.get("pid"),
            lines=req.query.get("lines", 1000),
            interval=req.query.get("interval"),
        )

        response = aiohttp.web.StreamResponse()
        response.content_type = "text/plain"
        await response.prepare(req)

        # try-except here in order to properly handle ongoing HTTP stream
        try:
            async for logs_in_bytes in self._log_api.stream_logs(options):
                await response.write(logs_in_bytes)
            await response.write_eof()
            return response
        except Exception as e:
            logger.exception(e)
            await response.write(b"Closing HTTP stream due to internal server error:\n")
            await response.write(str(e).encode())
            await response.write_eof()
            return response

    async def run(self, server):
        gcs_channel = self._dashboard_head.aiogrpc_gcs_channel
        self._state_api_data_source_client = StateDataSourceClient(gcs_channel)
        self._state_api = StateAPIManager(self._state_api_data_source_client)
        self._log_api = LogsManager(self._state_api_data_source_client)

    @staticmethod
    def is_minimal_module():
        return False
