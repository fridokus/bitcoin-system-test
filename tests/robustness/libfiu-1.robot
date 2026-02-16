*** Settings ***
Documentation    Test Bitcoin Core robustness with libfiu fault injection
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

*** Test Cases ***
Test Libfiu Fault Injection On Bitcoin Node
    [Documentation]    Test that a Bitcoin node can handle I/O faults injected by libfiu
    
    # Start generator node
    Clean Node Directory    ${GENERATOR_DIR}
    Start Bitcoin Node    ${GENERATOR_DIR}    ${GENERATOR_PORT}    daemon=${True}
    Wait For Node To Start    ${GENERATOR_DIR}
    
    # Create wallet and generate initial blocks
    Create Wallet    ${GENERATOR_DIR}    miner
    Generate Blocks    ${GENERATOR_DIR}    miner    150
    ${initial_count}=    Get Block Count    ${GENERATOR_DIR}
    Log    Generator node has ${initial_count} blocks
    Should Be Equal As Integers    ${initial_count}    150
    
    # Start victim node with fault injection
    Clean Node Directory    ${VICTIM_DIR}
    Start Bitcoin Node With Fault Injection    
    ...    ${BITCOIN_BIN}
    ...    ${VICTIM_DIR}
    ...    ${VICTIM_PORT}
    ...    ${VICTIM_RPC_PORT}
    ...    127.0.0.1:${GENERATOR_PORT}
    ...    probability=0.005
    Wait For Node To Start    ${VICTIM_DIR}    rpcport=${VICTIM_RPC_PORT}
    
    # Generate more blocks
    Generate Blocks    ${GENERATOR_DIR}    miner    10
    ${new_count}=    Get Block Count    ${GENERATOR_DIR}
    Log    Generator node now has ${new_count} blocks
    Should Be Equal As Integers    ${new_count}    160
    
    # Give victim time to sync
    Sleep    5s    Wait for victim to sync
    ${victim_count}=    Get Block Count    ${VICTIM_DIR}    rpcport=${VICTIM_RPC_PORT}
    Log    Victim node has ${victim_count} blocks
    
    # Stop victim node
    Stop Bitcoin Node    ${VICTIM_DIR}
    Sleep    2s
    
    # Restart victim with higher probability (testing recovery from existing state)
    Start Bitcoin Node With Fault Injection    
    ...    ${BITCOIN_BIN}
    ...    ${VICTIM_DIR}
    ...    ${VICTIM_PORT}
    ...    ${VICTIM_RPC_PORT}
    ...    127.0.0.1:${GENERATOR_PORT}
    ...    probability=0.01
    Wait For Node To Start    ${VICTIM_DIR}    rpcport=${VICTIM_RPC_PORT}
    
    # Verify victim can sync after restart with higher fault injection
    Sleep    5s    Wait for victim to sync after restart
    ${final_count}=    Get Block Count    ${VICTIM_DIR}    rpcport=${VICTIM_RPC_PORT}
    Log    Victim node synced to ${final_count} blocks after restart
    Should Be Equal As Integers    ${final_count}    ${new_count}

*** Keywords ***
Test Setup
    [Documentation]    Setup test environment
    
    Log    Setting up test environment
    Install Libfiu
    Download Bitcoin Core
    
    # Clean up any previous test directories
    Clean Node Directory    ${GENERATOR_DIR}
    Clean Node Directory    ${VICTIM_DIR}

Test Teardown
    [Documentation]    Clean up test environment
    
    Log    Cleaning up test environment
    Stop Bitcoin Node    ${GENERATOR_DIR}
    Stop Bitcoin Node    ${VICTIM_DIR}
    
    # Optional: Clean up directories
    Remove Directory    ${GENERATOR_DIR}    recursive=True
    Remove Directory    ${VICTIM_DIR}    recursive=True
