from force.process import ProcessMAR
import yaml
import numpy

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

if __name__ == "__main__":
    borehole_lat = -66.403
    borehole_lon = -63.212

    processor = ProcessMAR(borehole_lat, borehole_lon)
    borehole_MAR_data = processor.process()
