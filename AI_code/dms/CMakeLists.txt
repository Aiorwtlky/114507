cmake_minimum_required(VERSION 3.10)
project(driver_monitoring_system)

# 設定C++標準
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找OpenCV庫
find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})

# 添加源文件
set(SOURCES
    src/main.cpp
    src/camera.cpp
    src/face_detector.cpp
    src/drowsiness_detector.cpp
    src/posture_analyzer.cpp
)

# 添加可執行文件
add_executable(driver_monitor ${SOURCES})

# 連結OpenCV庫
target_link_libraries(driver_monitor ${OpenCV_LIBS})

# 確保可以找到頭文件
target_include_directories(driver_monitor PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

# 復制模型文件到輸出目錄
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/models/ DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/models/)

# 輸出信息
message(STATUS "OpenCV version: ${OpenCV_VERSION}")
message(STATUS "OpenCV include dirs: ${OpenCV_INCLUDE_DIRS}")
message(STATUS "OpenCV libraries: ${OpenCV_LIBS}")