from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, rmdir, rm
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.54.0"

class PackageConan(ConanFile):
    name = "openpam"
    description = "OpenPAM: an open source PAM library that focuses on simplicity, correctness, and cleanliness"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://openpam.org/"
    topics = ("pam", "pluggable-authentication-module", "authentication", "security")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD", "Neutrino"]:
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["pam"]
        self.cpp_info.system_libs = ["dl"]
