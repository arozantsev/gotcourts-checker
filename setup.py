import setuptools

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="gotcourts",
    version="0.1.0",
    # author="Example Author",
    # author_email="author@example.com",
    description="A small utility to list available slots on got courts website and send them to telegram channel",
    python_requires=">=3.6",
    install_requires=["aiohttp", "pyyaml", "python-telegram-bot"],
)
