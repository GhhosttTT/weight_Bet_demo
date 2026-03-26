# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - 充值成功后余额未更新
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped PBT Approach**: For deterministic bugs, scope the property to the concrete failing case(s) to ensure reproducibility
  - Test that when charge API returns success (`{"success":true,"amount":200.0}`), the user's availableBalance is immediately updated in the database
  - Test implementation: Create user with balance 0.0, call charge(200.0), verify charge returns success, immediately query balance, assert balance is still 0.0 (NOT 200.0)
  - The test assertions should match the Expected Behavior: balance SHOULD be oldBalance + chargeAmount, but on unfixed code it will still be oldBalance
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found: charge returns success but database balance unchanged, subsequent queries return old balance
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.3_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - 非充值成功场景的余额操作行为
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs (charge failures, balance queries, freeze/unfreeze, transfers, withdrawals)
  - Write property-based tests capturing observed behavior patterns:
    - When charge fails (amount <= 0 or payment gateway fails), balance remains unchanged
    - When querying balance, system returns accurate availableBalance and frozenBalance
    - When creating betting plan with sufficient balance, system correctly freezes funds (availableBalance decreases, frozenBalance increases)
    - When canceling plan, system correctly unfreezes funds (frozenBalance decreases, availableBalance increases)
    - When settlement transfer occurs, balance updates correctly
    - When withdrawal occurs, availableBalance decreases correctly
    - When balance is insufficient and no charge, system returns balance insufficient error
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 3. Fix for 充值后余额未更新

  - [x] 3.1 Implement backend charge endpoint fix
    - Locate the charge endpoint handler in backend (likely `backend/api/payments.py` or similar)
    - Add balance update logic after successful charge: query current balance, calculate newBalance = currentBalance + chargeAmount, update users.available_balance in database
    - Ensure transaction integrity: wrap charge record creation and balance update in same database transaction
    - Create transaction record: insert a 'charge' type transaction with amount, timestamp, and status
    - Return updated balance in response: add `newBalance` field to success response
    - Add logging: log user ID, charge amount, old balance, new balance before and after update
    - _Bug_Condition: isBugCondition(chargeResult, subsequentBalanceQuery) where chargeResult.success=true AND chargeResult.amount>0 AND subsequentBalanceQuery.availableBalance=previousBalance_
    - _Expected_Behavior: When charge returns success, availableBalance SHALL be updated to previousBalance + chargeAmount in database, and subsequent queries SHALL return updated balance_
    - _Preservation: All non-charge-success scenarios (charge failures, balance queries, freeze/unfreeze, transfers, withdrawals) SHALL maintain identical behavior_
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 3.2 (Optional) Implement client-side cache clearing
    - In `ChargeViewModel.kt`, after charge success, call `UserRepository.clearCache()` or `CacheManager.clearUserCache()` to clear local user info cache
    - Optionally, actively refresh balance by calling `UserRepository.getBalance(userId, forceRefresh=true)` after charge success
    - _Requirements: 2.1, 2.2_

  - [x] 3.3 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - 充值成功后余额立即更新
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - Verify that after charge success, balance query returns oldBalance + chargeAmount
    - Verify database users.available_balance is updated
    - Verify transaction record is created
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 3.4 Verify preservation tests still pass
    - **Property 2: Preservation** - 非充值成功场景的余额操作行为
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all preservation tests still pass after fix (no regressions in charge failures, balance queries, freeze/unfreeze, transfers, withdrawals)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 4. Checkpoint - Ensure all tests pass
  - Run all tests (bug condition test + preservation tests)
  - Verify bug condition test passes (balance updates after charge)
  - Verify all preservation tests pass (no regressions)
  - Test integration scenario: user with insufficient balance -> charge -> create betting plan -> verify plan created successfully and balance frozen correctly
  - Ask the user if questions arise
