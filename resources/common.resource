*** Settings ***
Documentation    High-level keywords for Bitcoin Core test scenarios
Library          ../resources/lib/bitcoin_core.py

*** Keywords ***
Setup Bitcoin Environment
    [Documentation]    Setup Bitcoin Core environment for testing
    Download Bitcoin Core

Setup Test Nodes
    [Documentation]    Setup generator and victim node directories
    [Arguments]    ${generator_dir}    ${victim_dir}
    Clean Node Directory    ${generator_dir}
    Clean Node Directory    ${victim_dir}

Initialize Generator Node
    [Documentation]    Start generator node and create wallet with initial blocks
    [Arguments]    ${datadir}    ${port}    ${wallet_name}    ${initial_blocks}
    Start Bitcoin Node    ${datadir}    ${port}
    Wait For Node To Start    ${datadir}
    Create Wallet    ${datadir}    ${wallet_name}
    Generate Blocks    ${datadir}    ${wallet_name}    ${initial_blocks}

Verify Block Count
    [Documentation]    Verify node has expected block count
    [Arguments]    ${datadir}    ${expected_count}    ${rpcport}=${None}
    ${actual_count}=    Get Block Count    ${datadir}    rpcport=${rpcport}
    Should Be Equal As Integers    ${actual_count}    ${expected_count}
    [Return]    ${actual_count}

Cleanup Test Environment
    [Documentation]    Stop nodes and clean up
    [Arguments]    ${generator_dir}    ${victim_dir}
    Stop Bitcoin Node    ${generator_dir}
    Stop Bitcoin Node    ${victim_dir}
