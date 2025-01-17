//===-- HostInfoTest.cpp ----------------------------------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "lldb/Host/HostInfo.h"
#include "TestingSupport/SubsystemRAII.h"
#include "TestingSupport/TestUtilities.h"
#include "lldb/Host/FileSystem.h"
#include "lldb/lldb-defines.h"
#include "llvm/Support/Host.h"
#include "gtest/gtest.h"

using namespace lldb_private;
using namespace llvm;

namespace {
class HostInfoTest : public ::testing::Test {
  SubsystemRAII<FileSystem, HostInfo> subsystems;
};
} // namespace

TEST_F(HostInfoTest, GetAugmentedArchSpec) {
  // Fully specified triple should not be changed.
  ArchSpec spec = HostInfo::GetAugmentedArchSpec("x86_64-pc-linux-gnu");
  EXPECT_EQ(spec.GetTriple().getTriple(), "x86_64-pc-linux-gnu");

  // Same goes if we specify at least one of (os, vendor, env).
  spec = HostInfo::GetAugmentedArchSpec("x86_64-pc");
  EXPECT_EQ(spec.GetTriple().getTriple(), "x86_64-pc");

  // But if we specify only an arch, we should fill in the rest from the host.
  spec = HostInfo::GetAugmentedArchSpec("x86_64");
  Triple triple(sys::getDefaultTargetTriple());
  EXPECT_EQ(spec.GetTriple().getArch(), Triple::x86_64);
  EXPECT_EQ(spec.GetTriple().getOS(), triple.getOS());
  EXPECT_EQ(spec.GetTriple().getVendor(), triple.getVendor());
  EXPECT_EQ(spec.GetTriple().getEnvironment(), triple.getEnvironment());

  // Test LLDB_ARCH_DEFAULT
  EXPECT_EQ(HostInfo::GetAugmentedArchSpec(LLDB_ARCH_DEFAULT).GetTriple(),
            HostInfo::GetArchitecture(HostInfo::eArchKindDefault).GetTriple());
}

TEST_F(HostInfoTest, GetHostname) {
  // Check non-empty string input works correctly.
  std::string s("abc");
  EXPECT_TRUE(HostInfo::GetHostname(s));
}
