#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2020-2020 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    osmTaxiStop.py
# @author  Michael Behrisch
# @date    2020-10-30

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import argparse
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
import sumolib


def main(options):
    net = sumolib.net.readNet(options.net_file)
    count = 0
    with open(options.output_file, "w") as output:
        sumolib.xml.writeHeader(output, root="additional")
        for n in sumolib.xml.parse(options.osm_file, "node"):
            name = None
            laneID = None
            length = options.length
            if n.tag:
                for t in n.tag:
                    if t.k == "capacity":
                        try:
                            length = max(int(t.v) * 7.5, length)
                        except ValueError:
                            pass
                    if t.k == "name":
                        name = t.v
                    if t.k == "amenity" and t.v == "taxi":
                        x, y = net.convertLonLat2XY(float(n.lon), float(n.lat))
                        for e, _ in sorted(net.getNeighboringEdges(x, y, options.radius), key=lambda i:i[1]):
                            for lane in e.getLanes():
                                if lane.getLength() > options.length and lane.allows(options.vclass):
                                    laneID = lane.getID() 
                if laneID:
                    print('    <%s id="%s_%s" name="%s" lane="%s" startPos="0" endPos="%s"/>' %
                          (options.type, options.type, count, name, laneID, options.length), file=output)
                    count += 1
        print("</additional>", file=output)


argParser = sumolib.options.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
argParser.add_argument("-s", "--osm-file", help="read OSM file from FILE (mandatory)", metavar="FILE")
argParser.add_argument("-n", "--net-file", help="read SUMO net from FILE (mandatory)", metavar="FILE")
argParser.add_argument("-o", "--output-file", help="write stopping places to the output FILE", metavar="FILE",
                       default="stopping_places.add.xml")
argParser.add_argument("-t", "--type", help="stopping place type", default="chargingStation")
argParser.add_argument("-r", "--radius", type=float, help="radius for edge finding", default=20.)
argParser.add_argument("-l", "--length", type=float, help="(minimum) length of the stopping place", default=20.)
argParser.add_argument("--vclass", help="which vehicle class should be allowed", default="passenger")
options = argParser.parse_args()
if not options.osm_file or not options.net_file:
    argParser.print_help()
    sys.exit()
main(options)
