from pathlib import Path
from spectran.utils import load_file, plot_psd
import matplotlib.pyplot as plt

def test_load_file():
    
    h5_file = Path(r"Q:\JanUllmann[JAN]\2024-09-26_Test\Voltage_amp_1e1.h5")

    output = load_file(h5_file)
    print(output)
    
if __name__ == "__main__":
    data = load_file(r"Q:\JanUllmann[JAN]\2024-09-26_Test\Voltage_amp_1e1.h5")
    plot_psd(data)