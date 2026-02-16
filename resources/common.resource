*** Settings ***
Documentation    Common keywords for Bitcoin Core operations
Library          Process
Library          OperatingSystem
Library          Collections
Library          String

*** Variables ***
${BITCOIN_VERSION}    30.2
${BITCOIN_DIR}        bitcoin-${BITCOIN_VERSION}
${BITCOIN_BIN}        ${BITCOIN_DIR}/bin/bitcoind
${BITCOIN_CLI}        ${BITCOIN_DIR}/bin/bitcoin-cli

*** Keywords ***
Download Bitcoin Core
    [Documentation]    Download and extract Bitcoin Core release
    [Arguments]    ${version}=${BITCOIN_VERSION}
    ${tarball}=    Set Variable    bitcoin-${version}-x86_64-linux-gnu.tar.gz
    ${url}=    Set Variable    https://bitcoincore.org/bin/bitcoin-core-${version}/${tarball}
    
    Log    Downloading Bitcoin Core ${version}
    Run Process    wget    -q    ${url}    shell=True
    Should Exist    ${tarball}
    
    Log    Extracting Bitcoin Core
    Run Process    tar    -xzf    ${tarball}    shell=True
    Should Exist    ${BITCOIN_DIR}

Start Bitcoin Node
    [Documentation]    Start a Bitcoin node in regtest mode
    [Arguments]    ${datadir}    ${port}    ${rpcport}=${EMPTY}    ${connect}=${EMPTY}    ${daemon}=${True}
    
    Log    Starting Bitcoin node with datadir=${datadir}, port=${port}
    
    ${cmd}=    Create List    ${BITCOIN_BIN}    -regtest    -datadir=${datadir}    -port=${port}    -bind=127.0.0.1
    
    Run Keyword If    '${rpcport}' != '${EMPTY}'    Append To List    ${cmd}    -rpcport=${rpcport}
    Run Keyword If    '${connect}' != '${EMPTY}'    Append To List    ${cmd}    -connect=${connect}
    Run Keyword If    ${daemon}    Append To List    ${cmd}    -daemon
    
    ${result}=    Run Process    @{cmd}
    Should Be Equal As Integers    ${result.rc}    0
    Sleep    2s    Wait for node to start

Stop Bitcoin Node
    [Documentation]    Stop a Bitcoin node
    [Arguments]    ${datadir}
    
    Log    Stopping Bitcoin node with datadir=${datadir}
    ${pid_file}=    Set Variable    ${datadir}/regtest/bitcoind.pid
    
    ${pid_exists}=    Run Keyword And Return Status    File Should Exist    ${pid_file}
    Run Keyword If    ${pid_exists}    Run Process    pkill    -F    ${pid_file}
    Sleep    1s    Wait for node to stop

Clean Node Directory
    [Documentation]    Remove all files in a node directory
    [Arguments]    ${datadir}
    
    Log    Cleaning directory ${datadir}
    Remove Directory    ${datadir}    recursive=True
    Create Directory    ${datadir}

Execute Bitcoin CLI
    [Documentation]    Execute bitcoin-cli command
    [Arguments]    ${datadir}    ${command}    ${rpcport}=${EMPTY}    ${rpcwallet}=${EMPTY}
    
    ${cmd}=    Create List    ${BITCOIN_CLI}    -regtest    -datadir=${datadir}
    
    Run Keyword If    '${rpcport}' != '${EMPTY}'    Append To List    ${cmd}    -rpcport=${rpcport}
    Run Keyword If    '${rpcwallet}' != '${EMPTY}'    Append To List    ${cmd}    -rpcwallet=${rpcwallet}
    
    @{command_parts}=    Split String    ${command}
    FOR    ${part}    IN    @{command_parts}
        Append To List    ${cmd}    ${part}
    END
    
    ${result}=    Run Process    @{cmd}
    Log    ${result.stdout}
    Should Be Equal As Integers    ${result.rc}    0
    [Return]    ${result.stdout}

Create Wallet
    [Documentation]    Create a wallet
    [Arguments]    ${datadir}    ${wallet_name}    ${rpcport}=${EMPTY}
    
    ${output}=    Execute Bitcoin CLI    ${datadir}    createwallet ${wallet_name}    rpcport=${rpcport}
    Log    Wallet created: ${output}

Generate Blocks
    [Documentation]    Generate blocks to an address
    [Arguments]    ${datadir}    ${wallet_name}    ${count}    ${rpcport}=${EMPTY}
    
    ${address}=    Execute Bitcoin CLI    ${datadir}    getnewaddress    rpcport=${rpcport}    rpcwallet=${wallet_name}
    ${address}=    Strip String    ${address}
    
    ${output}=    Execute Bitcoin CLI    ${datadir}    generatetoaddress ${count} ${address}    rpcport=${rpcport}    rpcwallet=${wallet_name}
    Log    Generated ${count} blocks: ${output}

Get Block Count
    [Documentation]    Get the current block count
    [Arguments]    ${datadir}    ${rpcport}=${EMPTY}
    
    ${output}=    Execute Bitcoin CLI    ${datadir}    getblockcount    rpcport=${rpcport}
    ${count}=    Strip String    ${output}
    [Return]    ${count}

Wait For Node To Start
    [Documentation]    Wait for node to be responsive
    [Arguments]    ${datadir}    ${rpcport}=${EMPTY}    ${timeout}=30
    
    FOR    ${i}    IN RANGE    ${timeout}
        ${status}=    Run Keyword And Return Status    Execute Bitcoin CLI    ${datadir}    getblockchaininfo    rpcport=${rpcport}
        Run Keyword If    ${status}    Return From Keyword
        Sleep    1s
    END
    Fail    Node did not start within ${timeout} seconds
