if (LIBCONFIG_INCLUDE_DIR AND LIBCONFIG_LIBRARY)
  set (LIBCONFIG_FOUND TRUE)
else (LIBCONFIG_INCLUDE_DIR AND LIBCONFIG_LIBRARY)
  find_path(LIBCONFIG_INCLUDE_DIR libconfig.h)
  find_library(LIBCONFIG_LIBRARY config)

  include(FindPackageHandleStandardArgs)

  find_package_handle_standard_args(LibConfig REQUIRED_VARS LIBCONFIG_INCLUDE_DIR LIBCONFIG_LIBRARY)
endif (LIBCONFIG_INCLUDE_DIR AND LIBCONFIG_LIBRARY)