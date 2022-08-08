# kraken-re

(Work in progress)

The `kraken-re` provides a rule engine to describe the components of a project. These components are translated into
build tasks using various rules.

_The rule engine is strongly inspired by [Pants](https://www.pantsbuild.org/docs/rules-api-and-target-api)._

## Concepts

### Targets

A Target is an addressable set of metadata. The metadata is comprised of *fields*. Each field is of a particular type,
and no two fields can be of the same type (subclasses of another field type are accepted).

### Field

A Field is a strongly typed description of a piece of data, such as "PythonProjectSourceDirectory". A field may be a
subclass of another field, allowing it to be taken into consideration when a generic request of fields matching its
parent class is requested.

### Rules

A rule describes how to translate a set of input types to an output type. Often, the inputs and output types will be
targets, but they can be arbitrary Python types. Every session begins with a set of initial objects that are usually
created by a script.

Every object in the rule system must be immutable and hashable. If two rules produce the same result, the results
are merged.

__Example script__

```py
docker_grpc_rust_template(name="template")
docker_image(dockerfile_target=":template", platforms=["linux/arm64", "linux/amd64"])
```

__Example rules__

```py
@rule
def get_dockerfile_resource_from_grpc_rust_template(request: DockerGrpcRustTemplateRequest) -> DockerfileResource:
    ...
    return DockerfileResource(path_to_dockerfile)

@rule
def get_docker_build_requests(image: DockerImageTarget) -> DockerBuildRequests:
    ...
    for platform in image[DockerPlatforms]:
        requests.append(...)
    return DockerBuildRequests(requests)

@rule
def build_docker(request: DockerBuildRequest) -> DockerBuildResult:
    ...
    return DockerBuildResult(...)
```

