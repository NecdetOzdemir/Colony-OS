from setuptools import setup

package_name = 'colony_config'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Colony-OS Team',
    maintainer_email='colony-os@example.com',
    description='Colony-OS merkezi konfigürasyon kütüphanesi',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={},
)
