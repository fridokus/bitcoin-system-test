*** Settings ***
Documentation    Test Bitcoin Core robustness with libfiu fault injection
Library          resources.lib.bitcoin_core.BitcoinCore
Library          resources.lib.robustness.RobustnessLib
Resource         ../../resources/common.resource
Resource         ../../resources/robustness.resource
Suite Setup      Test Setup
Suite Teardown   Test Teardown

*** Variables ***
${GENERATOR_DIR}    /tmp/node_generator
${VICTIM_DIR}       /tmp/node_victim
${GENERATOR_PORT}   18444
${VICTIM_PORT}      18445
${VICTIM_RPC_PORT}  18446
${WALLET_NAME}      miner

*** Test Cases ***
Test Libfiu Fault Injection On Bitcoin Node
    [Documentation]    Test that a Bitcoin node can handle I/O faults injected by libfiu
    
    # Initialize generator node with wallet and initial blocks
    Initialize Generator Node    ${GENERATOR_DIR}    ${GENERATOR_PORT}    ${WALLET_NAME}    150
    Verify Block Count    ${GENERATOR_DIR}    150
    
    # Start victim node with fault injection (uses retry logic)
    Start Victim Node With Retries    
    ...    ${VICTIM_DIR}
    ...    ${VICTIM_PORT}
    ...    ${VICTIM_RPC_PORT}
    ...    127.0.0.1:${GENERATOR_PORT}
    ...    0.005
    Wait For Node To Start    ${VICTIM_DIR}    rpcport=${VICTIM_RPC_PORT}
    
    # Generate more blocks on generator
    Generate Blocks    ${GENERATOR_DIR}    ${WALLET_NAME}    10
    Verify Block Count    ${GENERATOR_DIR}    160
    
    # Give victim time to sync
    Sleep    5s    Wait for victim to sync
    ${victim_count}=    Get Block Count    ${VICTIM_DIR}    rpcport=${VICTIM_RPC_PORT}
    Log    Victim node has ${victim_count} blocks
    
    # Monitor debug logs
    Tail Debug Log    ${VICTIM_DIR}    lines=50
    
    # Stop victim node
    Stop Bitcoin Node    ${VICTIM_DIR}
    Sleep    2s
    
    # Save debug logs from first run (Robot Framework sets OUTPUT_DIR)
    Copy Debug Log To    ${VICTIM_DIR}    ${OUTPUT_DIR}/victim_debug_first_run.log
    
    # Restart victim with higher probability (testing recovery from existing state)
    Start Victim Node With Retries
    ...    ${VICTIM_DIR}
    ...    ${VICTIM_PORT}
    ...    ${VICTIM_RPC_PORT}
    ...    127.0.0.1:${GENERATOR_PORT}
    ...    0.01
    Wait For Node To Start    ${VICTIM_DIR}    rpcport=${VICTIM_RPC_PORT}
    
    # Verify victim can sync after restart with higher fault injection
    Sleep    5s    Wait for victim to sync after restart
    ${final_count}=    Verify Block Count    ${VICTIM_DIR}    160    rpcport=${VICTIM_RPC_PORT}
    Log    Victim node synced to ${final_count} blocks after restart
    
    # Monitor debug logs after restart
    Tail Debug Log    ${VICTIM_DIR}    lines=50

*** Keywords ***
Test Setup
    [Documentation]    Setup test environment
    
    Log    Setting up test environment
    Log    Results will be saved to: ${OUTPUT_DIR}
    
    Setup Fault Injection Environment
    Setup Bitcoin Environment
    Setup Test Nodes    ${GENERATOR_DIR}    ${VICTIM_DIR}

Test Teardown
    [Documentation]    Clean up test environment and save debug logs
    
    Log    Saving debug logs for analysis
    Copy Debug Log To    ${GENERATOR_DIR}    ${OUTPUT_DIR}/generator_debug.log
    Copy Debug Log To    ${VICTIM_DIR}    ${OUTPUT_DIR}/victim_debug_final.log
    
    Log    Cleaning up test environment
    Stop Bitcoin Node    ${GENERATOR_DIR}
    Stop Bitcoin Node    ${VICTIM_DIR}
