// https://github.com/github/codeql/tree/main/cpp/ql/src/Metrics/Dependencies
import cpp
// https://github.com/github/codeql/blob/main/cpp/ql/lib/semmle/code/cpp/commons/Dependency.qll
import semmle.code.cpp.commons.Dependency

// https://github.com/github/codeql/blob/main/cpp/ql/lib/semmlecode.cpp.dbscheme#L143-L156
abstract class LibraryElement extends Element {
  abstract string getName();

  abstract string getVersion();

  abstract File getAFile();
}

/**
 * Anything that is to be considered a library.
 */
private newtype LibraryT =
  LibraryTElement(LibraryElement lib, string name, string version) {
    lib.getName() = name and
    lib.getVersion() = version
  } or
  LibraryTExternalPackage(@external_package ep, string name, string version) {
    exists(string package_name |
      external_packages(ep, _, package_name, version) and
      name = package_name
    )
  }

/**
 * A library that can have dependencies on it.
 */
class Library extends LibraryT {
  string name;
  string version;

  Library() {
    this = LibraryTElement(_, name, version) or
    this = LibraryTExternalPackage(_, name, version)
  }

  string getName() { result = name }

  string getVersion() { result = "unknown" }

  string toString() { result = getName() + "-" + getVersion() }

  File getAFile() {
    exists(LibraryElement lib |
      this = LibraryTElement(lib, _, _) and
      result = lib.getAFile()
    )
    or
    exists(@external_package ep |
      this = LibraryTExternalPackage(ep, _, _) and
      header_to_external_package(unresolveElement(result), ep)
    )
  }
}

/**
 * Generate the table of dependencies for the query (with some
 * packages that basically all projects depend on excluded).
 */
predicate encodedDependencies(File source, string encodedDependency) {
  exists(Library destLib |
    source = destLib.getAFile() and
    encodedDependency =
      "/" + source.getAbsolutePath() + "<|>" + destLib.getName() + "<|>" + destLib.getVersion()
  )
}

from File file, string encodedDependency
where encodedDependencies(file, encodedDependency)
select encodedDependency
