
import asyncio
import time


async def perform_task(name: str, delay: int):

    print(f"[START] {name}")

    await asyncio.sleep(delay)

    print(f"[END] {name}")

    return f"{name} completed"


# ---------------------------------
# Sequential execution
# ---------------------------------

async def run_sequential():

    print("\n=== SEQUENTIAL EXECUTION ===")

    start = time.perf_counter()

    result1 = await perform_task("Task A", 2)
    result2 = await perform_task("Task B", 2)
    result3 = await perform_task("Task C", 2)

    print("Results:", [result1, result2, result3])

    elapsed = time.perf_counter() - start

    print(f"Sequential time: {elapsed:.2f} seconds")


# ---------------------------------
# Concurrent execution
# ---------------------------------

async def run_concurrent():

    print("\n=== CONCURRENT EXECUTION ===")

    start = time.perf_counter()

    task1 = asyncio.create_task(
        perform_task("Task A", 2)
    )

    task2 = asyncio.create_task(
        perform_task("Task B", 2)
    )

    task3 = asyncio.create_task(
        perform_task("Task C", 2)
    )

    print("[DEBUG] All 3 tasks scheduled")

    results = await asyncio.gather(
        task1,
        task2,
        task3
    )

    print("Results:", results)

    elapsed = time.perf_counter() - start

    print(f"Concurrent time: {elapsed:.2f} seconds")


# ---------------------------------
# Main
# ---------------------------------

async def main():

    await run_sequential()

    await run_concurrent()


if __name__ == "__main__":
    asyncio.run(main())
