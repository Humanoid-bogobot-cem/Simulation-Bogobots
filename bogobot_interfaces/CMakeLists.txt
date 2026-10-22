cmake_minimum_required(VERSION 3.8)
project(bogobot_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Toma todos los .srv de srv/ y los .msg de msg/: basta con crear el archivo y recompilar.
file(GLOB interface_files RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} CONFIGURE_DEPENDS
  srv/*.srv
  msg/*.msg
)

if(interface_files)
  # Si un .srv usa tipos de otro paquete (p. ej. geometry_msgs/Point), agrega aquí
  # DEPENDENCIES geometry_msgs, y find_package(geometry_msgs REQUIRED) arriba.
  rosidl_generate_interfaces(${PROJECT_NAME}
    ${interface_files}
  )
else()
  message(WARNING "bogobot_interfaces: todavía no hay archivos en srv/ ni en msg/")
endif()

ament_export_dependencies(rosidl_default_runtime)
ament_package()
