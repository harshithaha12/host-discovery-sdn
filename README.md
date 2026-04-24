# Host Discovery Service using SDN

## Computer Networks Mini Project  
**Subject Code:** UE24CS252B  
**Project Title:** Host Discovery Service using Software Defined Networking (SDN)  
**Student Name:** Harshitha Vangaveti  
**SRN:** PES2UG24AM064  

---

# 1. Introduction

Software Defined Networking (SDN) is a modern networking approach in which the control plane is separated from the data plane. A centralized controller manages forwarding decisions, security policies, and network behavior.

This project implements a **Host Discovery Service using SDN** using **Mininet** and **Ryu Controller**. The controller dynamically discovers connected hosts, learns their locations, installs OpenFlow flow rules, forwards packets efficiently, blocks unauthorized traffic, and monitors network behavior.

---

# 2. Problem Statement

Traditional networks lack centralized visibility and dynamic control over connected hosts. Managing forwarding behavior, enforcing security policies, and monitoring traffic patterns becomes difficult.

The objective of this project is to design and implement a **Host Discovery Service using SDN** that dynamically identifies hosts connected to the network, learns their locations, controls forwarding behavior, applies access control policies, and observes network performance using Mininet and Ryu Controller.

---

# 3. Objectives

This project demonstrates:

- Controller–Switch Interaction  
- Flow Rule Design (Match–Action)  
- Host Discovery  
- Learning Switch Forwarding  
- Firewall / Access Control  
- Monitoring / Logging  
- Performance Evaluation using Ping and Iperf  

---

# 4. Features Implemented

## 1. Automatic Host Discovery

Whenever a host sends traffic for the first time, the controller automatically detects the host and registers it in the host database.

---

## 2. Host Database Maintenance

The controller maintains a real-time database containing:

- MAC Address
- IP Address
- Connected Switch
- Port Number

---

## 3. Dynamic Host Updates

If a host changes port or reconnects, the controller updates the host database automatically.

---

## 4. Learning Switch Forwarding

The controller learns MAC-to-port mappings and forwards packets intelligently.

- Known destination → direct forwarding  
- Unknown destination → flooding

---

## 5. Firewall / Access Control

Traffic from h3 to h1 is blocked by controller policy.

---

## 6. QoS Priority Flows

Traffic between h1 and h2 is assigned higher priority flow entries.

Priority:

- h1 ↔ h2 = 10
- Other traffic = 1

Example:

[QOS] High priority flow h1 <-> h2

---

## 7. Efficient Flow Management

Flow rules are installed only once and include idle timeout for cleanup.

Benefits:

- Reduces controller load
- Faster forwarding
- Better switch performance

---

## 8. Monitoring and Statistics

The controller continuously monitors traffic and prints packet counts.

---

# 5. Technologies Used

- Python 3  
- Ryu SDN Controller  
- Mininet  
- Open vSwitch  
- Ubuntu Linux  
- VMware Workstation Pro  
- GitHub  

---

# 6. System Requirements

## Hardware

- Minimum 4 GB RAM  
- Dual Core Processor  
- 20 GB Free Storage  

## Software

- Ubuntu 20.04 / 22.04  
- Python 3.x  
- pip3  
- Git  
- Internet Connection  

---

# 7. Prerequisites

Install the following:

- Python3  
- pip3  
- Git  
- Mininet  
- Open vSwitch  
- Ryu Controller  

---

# Setup, Installation and How to Run

```bash
sudo apt update
sudo apt upgrade -y
```
## Install Mininet

```bash
sudo apt install mininet -y
```
## Install Python and Python Tools

```bash
sudo apt install python3 python3-pip git -y
```
## Install Open vSwitch

```bash
sudo apt install openvswitch-switch -y
```
## Install Ryu Controller

```bash
pip3 install ryu
```
## Verify Mininet Installation

```bash
sudo mn
```
## Test Connectivity Inside Mininet

```bash
pingall
```
## Exit Mininet

```bash
exit
```
---

# How to Run the Project

## Start Ryu Controller

```bash
cd host-discovery-sdn
ryu-manager controller.py
```
<img width="738" height="278" alt="Screenshot 2026-04-20 203825" src="https://github.com/user-attachments/assets/cd81fc63-f3d5-4f77-9697-bdabc2a7dddd" />


## Start Mininet Topology

```bash
cd host-discovery-sdn
sudo mn --custom topo.py --topo simpletopo --controller remote
```
<img width="940" height="518" alt="image" src="https://github.com/user-attachments/assets/eabce5a1-293e-46ae-8786-3c48ba0ed41b" />


# Demo Commands

## Host Discovery

```bash
h1 ping -c 1 h2
```
## Allowed Communication

```bash
h1 ping -c 3 h2
```
<img width="940" height="261" alt="image" src="https://github.com/user-attachments/assets/3c181715-bcc2-428a-ba70-7b0db9ddeb92" />
<img width="940" height="392" alt="image" src="https://github.com/user-attachments/assets/f05aa205-1d56-4a91-8b11-234ffdb1845e" />



## Blocked Communication

```bash
h3 ping -c 3 h1
```
<img width="940" height="187" alt="image" src="https://github.com/user-attachments/assets/f17c3f03-9730-4a44-8643-c077f5afda25" />
<img width="940" height="547" alt="image" src="https://github.com/user-attachments/assets/c3423112-8f77-42d6-bde4-17150eea8aa1" />



## Full Connectivity Test

```bash
pingall
```
## Throughput Test

```bash
iperf h1 h2
```
<img width="940" height="99" alt="image" src="https://github.com/user-attachments/assets/bd0e0bf8-c781-42fc-b46a-be46549edabe" />


## Flow Rule Changes

```bash
sudo ovs-ofctl -O OpenFlow13 dump-flows s1
```
<img width="940" height="436" alt="image" src="https://github.com/user-attachments/assets/73f3add9-b9a2-4c41-b3b7-1a0cdb8a37dd" />


---
## exit 

'''bash
exit
'''
<img width="913" height="344" alt="image" src="https://github.com/user-attachments/assets/e775a65a-64ea-44dc-9b0c-535e6772421b" />


```

```
# 8. Conclusion

This project successfully demonstrates a Host Discovery Service using Software Defined Networking (SDN) using Mininet and the Ryu Controller. The controller dynamically discovers hosts, learns their locations, installs forwarding rules, and updates network information in real time. It also enforces firewall policies by blocking unauthorized communication and provides traffic prioritization through QoS-based flow rules.

By separating the control plane from the data plane, the project highlights how SDN enables centralized management, programmability, improved visibility, and efficient traffic handling. Overall, the implementation proves that SDN is a flexible and scalable approach for building intelligent and secure modern networks.
