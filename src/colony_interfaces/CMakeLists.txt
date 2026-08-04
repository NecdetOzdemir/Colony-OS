cmake_minimum_required(VERSION 3.8)
project(colony_interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)

# Tüm msg / srv / action dosyalarını kaydet
rosidl_generate_interfaces(${PROJECT_NAME}
  # Mesajlar
  "msg/Task.msg"
  "msg/Bid.msg"
  "msg/WorkerStatus.msg"
  # Servisler
  "srv/AssignTask.srv"
  # Actionlar
  "action/ExecuteTask.action"

  DEPENDENCIES std_msgs builtin_interfaces
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
