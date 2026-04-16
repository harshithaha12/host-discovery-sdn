#!/bin/bash

echo "Starting SDN Demo"

sudo mn -c

echo "Run controller in another terminal:"
echo "source ~/ryu-env/bin/activate"
echo "ryu-manager controller.py"

echo ""
echo "Then run:"
echo "sudo mn --custom topo.py --topo simpletopo --controller remote"