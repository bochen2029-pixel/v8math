cmake_minimum_required(VERSION 3.16)
project(v8math VERSION 1.0.0 LANGUAGES C CXX)

# v8math: bit-exact Node.js / V8 Math.* for C++ ports.
#   fdlibm::fdlibm  netlib fdlibm 5.3 with prefixed symbols (fdlibm/)
#   v8math::v8math  header-only wrapper with V8's Math.pow semantics (include/v8math/v8_math.hpp)
# Consumers: add_subdirectory(v8math) or, after cmake --install, find_package(v8math CONFIG REQUIRED);
# then target_link_libraries(<target> PRIVATE v8math::v8math).
# Compile the consumer with /fp:strict or /fp:precise (MSVC) or -ffp-contract=off (GCC/Clang); never fast-math.

option(V8MATH_BUILD_VERIFY "Build the verification harnesses (ctest needs node on PATH)" ON)

# node.exe links the UCRT statically, and the static libucrt and the system ucrtbase.dll do not round
# pow identically (33 of 100,009 samples differ by one ulp). When this project is built on its own,
# default to the static runtime so the verification matches node.exe; a consumer sets its own.
if(MSVC AND CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR AND NOT DEFINED CMAKE_MSVC_RUNTIME_LIBRARY)
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
    message(STATUS "v8math: using the static MSVC runtime so pow matches node.exe (set CMAKE_MSVC_RUNTIME_LIBRARY to override)")
endif()

add_subdirectory(fdlibm)

add_library(v8math INTERFACE)
add_library(v8math::v8math ALIAS v8math)
target_include_directories(v8math INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>)
target_link_libraries(v8math INTERFACE fdlibm::fdlibm)
target_compile_features(v8math INTERFACE cxx_std_11)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)
install(TARGETS v8math EXPORT v8mathTargets)
install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(EXPORT v8mathTargets NAMESPACE v8math:: DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/v8math)
write_basic_package_version_file("${CMAKE_CURRENT_BINARY_DIR}/v8mathConfigVersion.cmake"
    VERSION ${PROJECT_VERSION} COMPATIBILITY SameMajorVersion)
configure_package_config_file(cmake/v8mathConfig.cmake.in "${CMAKE_CURRENT_BINARY_DIR}/v8mathConfig.cmake"
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/v8math)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/v8mathConfig.cmake" "${CMAKE_CURRENT_BINARY_DIR}/v8mathConfigVersion.cmake"
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/v8math)

if(V8MATH_BUILD_VERIFY)
    enable_testing()
    add_executable(verify_fdlibm fdlibm/verify/verify_fdlibm.c)
    target_link_libraries(verify_fdlibm PRIVATE fdlibm::fdlibm)
    add_executable(verify_v8math fdlibm/verify/verify_v8math.cpp)
    target_link_libraries(verify_v8math PRIVATE v8math::v8math)
    target_compile_features(verify_v8math PRIVATE cxx_std_17)
    if(MSVC)
        target_compile_options(verify_fdlibm PRIVATE /fp:strict)
        target_compile_options(verify_v8math PRIVATE /fp:strict)
    else()
        target_compile_options(verify_fdlibm PRIVATE -ffp-contract=off)
        target_compile_options(verify_v8math PRIVATE -ffp-contract=off)
    endif()

    find_program(NODE_EXECUTABLE node)
    if(NODE_EXECUTABLE)
        # gen_ref.js samples the running Node; verify_v8math must then match it bit for bit.
        add_test(NAME v8math.gen_ref
                 COMMAND ${NODE_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/fdlibm/verify/gen_ref.js
                         ${CMAKE_CURRENT_BINARY_DIR}/ref_node.txt 20000)
        set_tests_properties(v8math.gen_ref PROPERTIES FIXTURES_SETUP node_reference)
        add_test(NAME v8math.verify COMMAND verify_v8math ${CMAKE_CURRENT_BINARY_DIR}/ref_node.txt)
        set_tests_properties(v8math.verify PROPERTIES FIXTURES_REQUIRED node_reference)
    else()
        message(STATUS "v8math: node not found, the verification test is not registered")
    endif()
endif()
