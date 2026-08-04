from setuptools import find_packages, setup

package_name = 'colony_logger'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Colony-OS Team',
    maintainer_email='colony-os@example.com',
    description='Colony-OS Performance and Data Logger',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'logger = colony_logger.logger_node:main'
        ],
    },
)
