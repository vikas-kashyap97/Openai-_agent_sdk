from openai import AsyncOpenAI
from agents import Agent, Runner, trace, set_default_openai_api, set_default_openai_client, set_trace_processors
from agents.tracing.processor_interface import TracingProcessor
from pprint import pprint
from dotenv import load_dotenv
load_dotenv()


client = AsyncOpenAI()
class LocalTraceProcessor(TracingProcessor):
    def __init__(self):
        self.traces = []
        self.spans = []

    def on_trace_start(self, trace):
        self.traces.append(trace)
        print(f"Trace started: {trace.trace_id}")

    def on_trace_end(self, trace):
        print(f"Trace ended: {trace.export()}")

    def on_span_start(self, span):
        self.spans.append(span)
        print(f"Span started: {span.span_id}")
        print(f"Span details: ")
        pprint(span.export())

    def on_span_end(self, span):
        print(f"Span ended: {span.span_id}")
        print(f"Span details:")
        pprint(span.export())

    def force_flush(self):
        print("Forcing flush of trace data")

    def shutdown(self):
        print("=======Shutting down trace processor========")
        # Print all collected trace and span data
        print("Collected Traces:")
        for trace in self.traces:
            print(trace.export())
        print("Collected Spans:")
        for span in self.spans:
            print(span.export())


# Configure the client
set_default_openai_client(client=client, use_for_tracing=True)
set_default_openai_api("chat_completions")

# Set up the custom trace processor
local_processor = LocalTraceProcessor()
set_trace_processors([local_processor])





async def main():
    agent = Agent(
    name="Assistant",
    instructions="You are an expert of agentic AI.",
    )

    with trace("Example workflow"):
        first_result = await Runner.run(agent, "Start the task")
        second_result = await Runner.run(agent, f"Rate this result: {first_result.final_output}")
        print(f"Result: {first_result.final_output}")
        print(f"Rating: {second_result.final_output}")

# Run the main function
import asyncio
asyncio.run(main())



# You can see the whole documentation for creating local trace processors here: (https://openai.github.io/openai-agents-python/tracing/)