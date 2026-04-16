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

# 4. Technologies Used

- Python 3  
- Ryu SDN Controller  
- Mininet  
- Open vSwitch  
- Ubuntu Linux  
- VMware Workstation Pro  
- GitHub  

---

# 5. System Requirements

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

# 6. Prerequisites

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

## Install Mininet

```bash
sudo apt install mininet -y

## Install Python and Python Tools

```bash
sudo apt install python3 python3-pip git -y

## Install Open vSwitch

```bash
sudo apt install openvswitch-switch -y

## Install Ryu Controller

```bash
pip3 install ryu

## Verify Mininet Installation

```bash
sudo mn

## Test Connectivity Inside Mininet

```bash
pingall

## Exit Mininet

```bash
exit

---

# How to Run the Project

## Start Ryu Controller

```bash
cd host-discovery-sdn
ryu-manager controller.py

## Start Mininet Topology

```bash
cd host-discovery-sdn
sudo mn --custom topo.py --topo simpletopo --controller remote


# Demo Commands

## Allowed Communication

```bash
h1 ping -c 3 h2

## Blocked Communication

```bash
h3 ping -c 3 h1

## Full Connectivity Test

```bash
pingall

## Throughput Test

```bash
iperf h1 h2

## Flow Rule Changes

```bash
sudo ovs-ofctl -O OpenFlow13 dump-flows s1