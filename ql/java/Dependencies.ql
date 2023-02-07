import java
// https://github.com/github/codeql/blob/main/java/ql/lib/semmle/code/java/DependencyCounts.qll
import semmle.code.java.DependencyCounts

predicate fileJarDependencyCount(File sourceFile, int total, string entity) {
  exists(Container targetJar, string jarStem |
    jarStem = targetJar.getStem() and
    targetJar.(File).getExtension() = "jar"
  |
    total =
      strictsum(RefType r, RefType dep, int num |
        r.getFile() = sourceFile and
        r.fromSource() and
        dep.getFile().getParentContainer*() = targetJar and
        numDepends(r, dep, num)
      |
        num
      ) and
    exists(string name, string version |
      if hasDashedVersion(jarStem, _, _)
      then hasDashedVersion(jarStem, name, version)
      else (
        name = jarStem and version = "unknown"
      )
    |
      entity = targetJar + "<|>" + name + "<|>" + version
    )
  )
}

from File sourceFile, string entity
where fileJarDependencyCount(sourceFile, _, entity)
select entity
