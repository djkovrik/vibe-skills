"""Resolve a reviewed Gradle project graph into a transitive check scope."""
from scoped_evidence import patterns_valid
from vibe_protocol import ProtocolError


def resolve_modules(modules, graph):
    if not modules or not isinstance(graph, dict):
        raise ProtocolError('modules and reviewed moduleGraph required')
    visited, patterns = set(), []
    def visit(name):
        if name in visited: return
        if name not in graph: raise ProtocolError(f'unknown module dependency: {name}')
        visited.add(name)
        node = graph[name]
        directory = node.get('directory', '')
        if not directory or directory == '.': raise ProtocolError('module directory must be explicit')
        patterns.extend(patterns_valid([directory.rstrip('/') + '/**']))
        for dependency in node.get('dependencies', []): visit(dependency)
    for module in modules: visit(module)
    return sorted(set(patterns)), sorted(visited)
