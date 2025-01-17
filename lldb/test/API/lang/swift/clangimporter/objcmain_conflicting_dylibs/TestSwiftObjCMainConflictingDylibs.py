# TestSwiftObjCMainConflictingDylibs.py
#
# This source file is part of the Swift.org open source project
#
# Copyright (c) 2018 Apple Inc. and the Swift project authors
# Licensed under Apache License v2.0 with Runtime Library Exception
#
# See https://swift.org/LICENSE.txt for license information
# See https://swift.org/CONTRIBUTORS.txt for the list of Swift project authors
#
# ------------------------------------------------------------------------------

import lldb
from lldbsuite.test.lldbtest import *
from lldbsuite.test.decorators import *
import lldbsuite.test.lldbutil as lldbutil
import os
import unittest2
import shutil

class TestSwiftObjCMainConflictingDylibs(TestBase):

    mydir = TestBase.compute_mydir(__file__)

    def setUp(self):
        TestBase.setUp(self)

    # Don't run ClangImporter tests if Clangimporter is disabled.
    @skipIf(setting=('symbols.use-swift-clangimporter', 'false'))
    @skipUnlessDarwin
    @swiftTest
    def test(self):
        # To ensure we hit the rebuild problem remove the cache to avoid caching.
        mod_cache = self.getBuildArtifact("my-clang-modules-cache")
        if os.path.isdir(mod_cache):
          shutil.rmtree(mod_cache)

        self.runCmd('settings set symbols.clang-modules-cache-path "%s"'
                    % mod_cache)
        self.build()
        exe_name = "a.out"
        exe = self.getBuildArtifact(exe_name)

        # Create the target
        target = self.dbg.CreateTarget(exe)
        self.assertTrue(target, VALID_TARGET)

        self.registerSharedLibrariesWithTarget(target, ['Foo', 'Bar'])

        # Set the breakpoints
        bar_breakpoint = target.BreakpointCreateBySourceRegex(
            'break here', lldb.SBFileSpec('Bar.swift'))
        foo_breakpoint = target.BreakpointCreateBySourceRegex(
            'break here', lldb.SBFileSpec('Foo.swift'))

        process = target.LaunchSimple(None, None, os.getcwd())
        process.Continue()
        # Prime the module cache with the Foo variant.
        self.expect("fr var baz", "correct baz", substrs=["i_am_from_Foo"])
        self.assertTrue(os.path.isdir(mod_cache), "module cache exists")

        # Restart.
        process = target.LaunchSimple(None, None, os.getcwd())
        # This is failing because the Target-SwiftASTContext uses the
        # amalgamated target header search options from all dylibs.
        self.expect("p baz", "wrong baz", substrs=["i_am_from_Foo"])
        self.expect("fr var baz", "wrong baz", substrs=["i_am_from_Foo"])


        process.Continue()
        self.expect("p baz", "correct baz", substrs=["i_am_from_Foo"])
        self.expect("fr var baz", "correct baz", substrs=["i_am_from_Foo"])
        

if __name__ == '__main__':
    import atexit
    lldb.SBDebugger.Initialize()
    atexit.register(lldb.SBDebugger.Terminate)
    unittest2.main()
