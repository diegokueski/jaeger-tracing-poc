# Lesson 2 - Context and Tracing Functions

## Run code
python -m lesson02.hello Diego

## Objectives

Learn how to:

* Trace individual functions
* Combine multiple spans into a single trace
* Propagate the in-process context

## Walkthrough

First, copy your work or the official solution from [Lesson 1](../lesson01) to `lesson02/exercise/hello.py`,
and make it a module by creating the `__init__.py` file:

```
mkdir lesson02/exercise
touch lesson02/exercise/__init__.py
cp lesson01/solution/*.py lesson02/exercise/
```

### Tracing individual functions

In [Lesson 1](../lesson01) we wrote a program that creates a trace that consists of a single span.
That single span combined two operations performed by the program, formatting the output string
and printing it. Let's move those operations into standalone functions first:

```python
def say_hello(hello_to):
    with tracer.start_span('say-hello') as span:
        span.set_tag('hello-to', hello_to)
        hello_str = format_string(span, hello_to)
        print_hello(span, hello_str)

def format_string(span, hello_to):
    hello_str = 'Hello, %s!' % hello_to
    span.log_kv({'event': 'string-format', 'value': hello_str})
    return hello_str

def print_hello(span, hello_str):
    print(hello_str)
    span.log_kv({'event': 'println'})
```

Of course, this does not change the outcome. What we really want to do is to wrap each function into its own span.

```python
def format_string(root_span, hello_to):
    with tracer.start_span('format') as span:
        hello_str = 'Hello, %s!' % hello_to
        span.log_kv({'event': 'string-format', 'value': hello_str})
        return hello_str

def print_hello(root_span, hello_str):
    with tracer.start_span('println') as span:
        print(hello_str)
        span.log_kv({'event': 'println'})
```

Let's run it:

```
$ python -m lesson02.exercise.hello Bryan
Initializing Jaeger Tracer with UDP reporter
Using sampler ConstSampler(True)
opentracing.tracer initialized to <jaeger_client.tracer.Tracer object at 0x10d0bcf10>[app_name=hello-world]
Reporting span a5224a80cebaee4:a5224a80cebaee4:0:1 hello-world.format
Hello, Bryan!
Reporting span 947f0ad168b588aa:947f0ad168b588aa:0:1 hello-world.println
Reporting span 7fe927d093e3e33c:7fe927d093e3e33c:0:1 hello-world.say-hello
```

We got three spans, but there is a problem here. The first hexadecimal segment of the output represents
Jaeger trace ID, yet they are all different. If we search for those IDs in the UI each one will represent
a standalone trace with a single span. That's not what we wanted!

What we really wanted was to establish causal relationship between the two new spans to the root
span started in `main`. We can do that by passing an additional option to the `start_span`
function:

```python
def format_string(root_span, hello_to):
    with tracer.start_span('format', child_of=root_span) as span:
        hello_str = 'Hello, %s!' % hello_to
        span.log_kv({'event': 'string-format', 'value': hello_str})
        return hello_str
```

If we think of the trace as a directed acyclic graph where nodes are the spans and edges are
the causal relationships between them, then the `child_of` option is used to create one such
edge between `span` and `root_span`. In the API the edges are represented by `SpanReference` type
that consists of a `SpanContext` and a label. The `SpanContext` represents an immutable, thread-safe
portion of the span that can be used to establish references or to propagate it over the wire.
The label, or `ReferenceType`, describes the nature of the relationship. `ChildOf` relationship
means that the `root_span` has a logical dependency on the child `span` before `root_span` can
complete its operation. Another standard reference type in OpenTracing is `FollowsFrom`, which
means the `root_span` is the ancestor in the DAG, but it does not depend on the completion of the
child span, for example if the child represents a best-effort, fire-and-forget cache write.

If we modify the `print_hello` function accordingly and run the app, we'll see that all reported
spans now belong to the same trace:

```
$ python -m lesson02.exercise.hello Bryan
Initializing Jaeger Tracer with UDP reporter
Using sampler ConstSampler(True)
opentracing.tracer initialized to <jaeger_client.tracer.Tracer object at 0x1049f4f10>[app_name=hello-world]
Reporting span 8d7ec03b285a2401:9a9ce59c4112c038:8d7ec03b285a2401:1 hello-world.format
Hello, Bryan!
Reporting span 8d7ec03b285a2401:b67d23e2bebfe48c:8d7ec03b285a2401:1 hello-world.println
Reporting span 8d7ec03b285a2401:8d7ec03b285a2401:0:1 hello-world.say-hello
```

We can also see that instead of `0` in the 3rd position the first two reported spans display
`8d7ec03b285a2401`, which is the ID of the root span. The root span is reported last because
it is the last one to finish.

If we find this trace in the UI, it will show a proper parent-child relationship between the spans.

### Propagate the in-process context

You may have noticed one unpleasant side effect of our recent changes - we had to pass the Span object
as the first argument to each function. Unlike Go, languages like Java and Python support thread-local
storage, which is convenient for storing such request-scoped data like the current span. As of v2 the OpenTracing API for Python supports a standard mechanism for passing and accessing the current span using the concepts of Scope Manager and Scope, which are using either plain thread-local storage or more specific mechanisms provided by various async frameworks like `tornado` or `gevent`. 

Instead of calling `start_span` on the tracer, we can call `start_active_span` that invokes that mechanism and makes the span "active" and accessible via `tracer.active_span`. The return value of the `start_active_span` is a `Scope` object that needs to be closed in order to restore the previously active span on the stack.

```python
def say_hello(hello_to):
    with tracer.start_active_span('say-hello') as scope:
        scope.span.set_tag('hello-to', hello_to)
        hello_str = format_string(hello_to)
        print_hello(hello_str)
```

Notice that we're no longer passing the span as argument to the functions, because they can now
retrieve the span with `tracer.active_span` function. However, because creating a child span of a currently active span is such a common pattern, this now happens automatically, so that we do not need to pass the `child_of` reference to the parent span anymore:

```python
def format_string(hello_to):
    with tracer.start_active_span('format') as scope:
        hello_str = 'Hello, %s!' % hello_to
        scope.span.log_kv({'event': 'string-format', 'value': hello_str})
        return hello_str

def print_hello(hello_str):
    with tracer.start_active_span('println') as scope:
        print(hello_str)
        scope.span.log_kv({'event': 'println'})
```

Note that because `start_active_span` function returns a `Scope` instead of a `Span`, we use `scope.span` property to access the span when we want to annotate it with tags or logs. We could also use `tracer.active_span` property with the same effect.

If we run this modified program, we will see that all three reported spans still have the same trace ID.

### What's the Big Deal?

The last change we made may not seem particularly useful. But imagine that your program is
much larger with many functions calling each other. By using the Scope Manager mechanism we can access
the current span from any place in the program without having to pass the span object as the argument to
all the function calls. This is especially useful if we are using instrumented RPC frameworks that perform
tracing functions automatically - they have a stable way of finding the current span.

## Conclusion

The complete program can be found in the [solution](./solution) package.

Next lesson: [Tracing RPC Requests](../lesson03).