cmake_minimum_required(VERSION 3.5)
project(SimpleSpreadsheetGUI)

# Fetch Raylib
include(FetchContent)
FetchContent_Declare(
    raylib
    GIT_REPOSITORY https://github.com/raysan5/raylib.git
    GIT_TAG 4.5.0  # Replace with the desired version
)
FetchContent_MakeAvailable(raylib)

# Add executable
add_executable(SimpleSpreadsheetGUI src/app.c)

# Link Raylib to the executable
target_link_libraries(SimpleSpreadsheetGUI raylib)

# Add required flags for different platforms
if (CMAKE_SYSTEM_NAME STREQUAL "Windows")
    target_link_libraries(SimpleSpreadsheetGUI winmm.lib)
elseif (CMAKE_SYSTEM_NAME STREQUAL "Linux")
    target_link_libraries(SimpleSpreadsheetGUI pthread m dl)
endif()

# Set C standard
set_property(TARGET SimpleSpreadsheetGUI PROPERTY C_STANDARD 99)
