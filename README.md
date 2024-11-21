# Quorus

A lightweight, batteries included, concurrency manager built in python. 

### What it does

Quorus provides system, network, and cloud engineers a tool for deploying a configurable concurrency manager for high availability systems. 

Quorus is deployed locally on any system or appliance and uses the Raft concurrency algorithm to ensure at most one "leader" node is present at any time. Quorus extends the normal capbilities of Raft by allowing for user configurable roles that can be integrated into the Raft election system. This allows users to apply Infrastructure as Code (Iac) Principals to configure specialized and automatable roles that can be assumed and transfered between nodes. Quorus shines most in environments where remote management is not possible and where systems need to be able to operate and reduced capacities for extended periods.


