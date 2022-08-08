import setuptools

setuptools.setup(
    name="LudlPy",
    version="0.0.1",
    author="Jayden Roberts",
    author_email="jayden.p.roberts@gmail.com",
    description="A Python interface for the Ludl MAC 2002 controller",
    url="https://github.com/JaydenR2305/LudlPy",
    project_urls={
        "Bug Tracker": "https://github.com/JaydenR2305/LudlPy/issues"
    },
    license="MIT",
    packages=setuptools.find_packages(),
    install_requires=["pyserial"],
)
