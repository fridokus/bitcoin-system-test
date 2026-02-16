*** Settings ***
Documentation    Keywords for fault injection with libfiu
Library          Process
Library          OperatingSystem

*** Keywords ***
Install Libfiu
    [Documentation]    Install libfiu development package and utilities
    
    Log    Installing libfiu-dev and fiu-utils
    ${result}=    Run Process    sudo    apt-get    update    -qq
    ${result}=    Run Process    sudo    apt-get    install    -y    libfiu-dev    fiu-utils
    Should Be Equal As Integers    ${result.rc}    0
    Log    libfiu installed successfully

Start Bitcoin Node With Fault Injection
    [Documentation]    Start a Bitcoin node with libfiu fault injection
    [Arguments]    ${bitcoind_path}    ${datadir}    ${port}    ${rpcport}    ${connect}    ${probability}=0.005
    
    Log    Starting Bitcoin node with fault injection (probability=${probability})
    
    ${fault_spec}=    Set Variable    enable_random name=posix/io/*,probability=${probability}
    
    ${cmd}=    Catenate    SEPARATOR=    
    ...    fiu-run -x -c "${fault_spec}" 
    ...    ${bitcoind_path} -regtest -datadir=${datadir} -port=${port} -rpcport=${rpcport} -connect=${connect} -daemon
    
    ${result}=    Run Process    ${cmd}    shell=True
    Log    ${result.stdout}
    Log    ${result.stderr}
    Should Be Equal As Integers    ${result.rc}    0
    Sleep    3s    Wait for node to start with fault injection
