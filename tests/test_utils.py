from pathlib import Path
import spectran.utils as spu
import pyqtgraph as pg

def test_load_file():
    
    h5_file = Path(r"Q:\JanUllmann[JAN]\2024-09-26_Test\Voltage_amp_1e1.h5")

    output = spu.load_file(h5_file)
    
def test_plotting():
    data = spu.load_file(r"Q:\JanUllmann[JAN]\2024-09-26_Test\Voltage_amp_1e1.h5")
    plot = spu.plot_psd(data)
    spu.plot_psd(data, plot=plot)
    spu.plot([1,2,3,4,5], [12,.343,34.,34,14], 
             plot=plot, 
             pen=pg.mkPen(width=.5, color="r"))
    
if __name__ == "__main__":
    test_plotting()
    spu.show()
    