import sys, sherpa_onnx, soundfile as sf, os
D=os.path.dirname(os.path.abspath(__file__))+"/dl/"
def make(voice):
    d=D+voice+"/"
    onnx=[f for f in os.listdir(d) if f.endswith(".onnx")][0]
    cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=d+onnx,tokens=d+"tokens.txt",data_dir=d+"espeak-ng-data",
             noise_scale=0.6, noise_scale_w=0.7, length_scale=1.0),num_threads=4))
    return sherpa_onnx.OfflineTts(cfg)
if __name__=="__main__":
    voice,text,out,speed=sys.argv[1],sys.argv[2],sys.argv[3],float(sys.argv[4]) if len(sys.argv)>4 else 1.0
    t=make(voice); a=t.generate(text,sid=0,speed=speed); import numpy as np; s=np.array(a.samples,dtype=np.float32); print("n",len(s)); sf.write(out,s,a.sample_rate); print(out,len(a.samples)/a.sample_rate)
