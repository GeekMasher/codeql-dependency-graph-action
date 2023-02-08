// https://github.com/github/codeql/blob/7f096845773d411f6b3e898c06311969308bbd91/python/ql/src/Metrics/Dependencies/ExternalDependencies.ql
import python
import semmle.python.dependencies.TechInventory

predicate src_package_count(File sourceFile, ExternalPackage package, int total) {
  total =
    strictcount(AstNode src |
      dependency(src, package) and
      src.getLocation().getFile() = sourceFile
    )
}

from File sourceFile, int total, string entity, ExternalPackage package
where
  src_package_count(sourceFile, package, total) and
  entity = munge(sourceFile, package)
select entity
