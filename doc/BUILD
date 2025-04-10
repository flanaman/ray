load("//bazel:python.bzl", "py_test_run_all_subdirectory")
load("//bazel:python.bzl", "py_test_run_all_notebooks")

exports_files(["test_myst_doc.py"])

# --------------------------------------------------------------------
# Tests from the doc directory.
# Please keep these sorted alphabetically, but start with the
# root directory.
# --------------------------------------------------------------------

# Support for Dask has been dropped in 3.6.
py_test(
    name = "dask_xgboost",
    size = "medium",
    main = "test_myst_doc.py",
    srcs = ["test_myst_doc.py"],
    tags = ["exclusive", "team:ml", "py37"],
    data = ["//doc/source/ray-core/examples:core_examples"],
    args = ["--path", "doc/source/ray-core/examples/dask_xgboost/dask_xgboost.ipynb",
            "--smoke-test", "--address ''", "--num-actors 4", "--cpus-per-actor 1", "--num-actors-inference 4",
            "--cpus-per-actor-inference 1"]
)

# Support for Modin has been dropped in 3.6.
py_test(
    name = "modin_xgboost",
    size = "medium",
    main = "test_myst_doc.py",
    srcs = ["test_myst_doc.py"],
    tags = ["exclusive", "team:ml", "py37"],
    data = ["//doc/source/ray-core/examples:core_examples"],
    args = ["--path", "doc/source/ray-core/examples/modin_xgboost/modin_xgboost.ipynb",
            "--smoke-test", "--address ''", "--num-actors 4",
            "--cpus-per-actor 1", "--num-actors-inference 4",
            "--cpus-per-actor-inference 1"]
)

### Ray Data
py_test(
    name = "quick_start",
    size = "small",
    srcs = ["source/data/doc_code/quick_start.py"],
    tags = ["exclusive", "team:ml"]
)

py_test(
    name = "big_data_ingestion",
    size = "small",
    main = "test_myst_doc.py",
    srcs = ["test_myst_doc.py"],
    args = ["--path", "doc/source/data/examples/big_data_ingestion.ipynb"],
    data = ["//doc/source/data/examples:data_examples"],
    tags = ["exclusive", "team:core", "py37"]
)

py_test(
    name = "datasets_train",
    size = "medium",
    srcs = ["source/ray-core/_examples/datasets_train/datasets_train.py"],
    tags = ["exclusive", "team:ml", "py37", "datasets_train"],
    args = ["--smoke-test", "--num-workers=2", "--use-gpu"]
)

py_test(
    name = "plot_hyperparameter",
    size = "small",
    main = "test_myst_doc.py",
    srcs = ["test_myst_doc.py"],
    args = ["--path", "doc/source/ray-core/examples/plot_hyperparameter.ipynb"],
    data = ["//doc/source/ray-core/examples:core_examples"],
    tags = ["exclusive", "team:ml"]
)

py_test(
    name = "plot_parameter_server",
    size = "medium",
    main = "test_myst_doc.py",
    srcs = ["test_myst_doc.py"],
    args = ["--path", "doc/source/ray-core/examples/plot_parameter_server.ipynb"],
    data = ["//doc/source/ray-core/examples:core_examples"],
    tags = ["exclusive", "team:ml"]
)

py_test(
    name = "plot_pong_example",
    size = "large",
    main = "test_myst_doc.py",
    srcs = ["test_myst_doc.py"],
    args = ["--path", "doc/source/ray-core/examples/plot_pong_example.ipynb"],
    data = ["//doc/source/ray-core/examples:core_examples"],
    tags = ["exclusive", "team:ml"]
)

# --------------------------------------------------------------------
# Test all doc/source/ray-core/doc_code code included in rst/md files.
# --------------------------------------------------------------------

py_test(
    name = "doc_code_tf_example",
    size = "small",
    main = "source/ray-core/doc_code/tf_example.py",
    srcs = ["source/ray-core/doc_code/tf_example.py"],
    tags = ["exclusive", "tf", "team:ml"]
)

py_test(
    name = "doc_code_torch_example",
    size = "small",
    main = "source/ray-core/doc_code/torch_example.py",
    srcs = ["source/ray-core/doc_code/torch_example.py"],
    tags = ["exclusive", "pytorch", "team:ml"]
)

py_test(
    name = "doc_code_metrics_example",
    size = "small",
    main = "source/ray-core/doc_code/metrics_example.py",
    srcs = ["source/ray-core/doc_code/metrics_example.py"],
    tags = ["exclusive", "team:serve"]
)

py_test(
    name = "doc_code_runtime_env_example",
    size = "small",
    main = "source/ray-core/doc_code/runtime_env_example.py",
    srcs = ["source/ray-core/doc_code/runtime_env_example.py"],
    tags = ["exclusive", "post_wheel_build", "team:serve"]
)

# --------------------------------------------------------------------
# Test all doc/source/serve/doc_code code included in rst/md files.
# --------------------------------------------------------------------

py_test_run_all_subdirectory(
    size = "medium",
    include = ["source/serve/doc_code/*.py"],
    exclude = [],
    extra_srcs = [],
    tags = ["exclusive", "team:serve"],
)



# --------------------------------------------------------------------
# Test all doc/source/tune/doc_code code included in rst/md files.
# --------------------------------------------------------------------

py_test_run_all_subdirectory(
    size = "medium",
    include = ["source/tune/doc_code/*.py"],
    exclude = [],
    extra_srcs = [],
    tags = ["exclusive", "team:ml"],
)

# --------------------------------------------------------------------
# Test all doc/source/rllib/doc_code code included in rst/md files.
# --------------------------------------------------------------------

py_test_run_all_subdirectory(
    size = "medium",
    include = ["source/rllib/doc_code/*.py"],
    exclude = [],
    extra_srcs = [],
    tags = ["exclusive", "team:ml"],
)

# --------------------------------------------------------------------
# Test all doc/source/ray-air/doc_code code included in rst/md files.
# --------------------------------------------------------------------

py_test_run_all_subdirectory(
    size = "large",
    include = ["source/ray-air/doc_code/*.py"],
    exclude = [],
    extra_srcs = [],
    tags = ["exclusive", "team:ml"],
)

# --------------------------------------------------------------------
# Test all doc/source/ray-overview/doc_test snippets, used on ray.io
# --------------------------------------------------------------------

py_test_run_all_subdirectory(
    size = "small",
    include = ["source/ray-overview/doc_test/*.py"],
    exclude = ["source/ray-overview/doc_test/ray_data.py"],
    extra_srcs = [],
    tags = ["exclusive", "team:ml"],
)
