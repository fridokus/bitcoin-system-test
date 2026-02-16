*** Settings ***
Documentation    High-level keywords for robustness testing with fault injection
Library          ../resources/lib/robustness.py

*** Keywords ***
Setup Fault Injection Environment
    [Documentation]    Install and setup fault injection tools
    Install Libfiu

Start Victim Node With Retries
    [Documentation]    Start victim node with fault injection and automatic retries
    [Arguments]    ${datadir}    ${port}    ${rpcport}    ${connect_addr}    ${probability}
    Start Victim Node With Fault Injection    ${datadir}    ${port}    ${rpcport}    ${connect_addr}    probability=${probability}
