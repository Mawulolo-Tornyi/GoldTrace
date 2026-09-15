from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from .config import ROOT
from .audio_model import AudioCNN
from .vibration_model import VibrationCNN
from .utils import write_json


def _verify_onnx(path:Path, input_name:str, sample:np.ndarray, torch_output:np.ndarray)->dict:
    try:
        import onnxruntime as ort
        session=ort.InferenceSession(str(path),providers=['CPUExecutionProvider'])
        edge=session.run(None,{input_name:sample.astype(np.float32)})[0]
        diff=float(np.max(np.abs(edge-torch_output)))
        return {'verified':bool(diff<1e-4),'max_abs_difference':diff}
    except Exception as exc:
        return {'verified':False,'reason':f'ONNX Runtime verification unavailable: {exc}'}


def _export_torchscript(model, dummy, path:Path)->dict:
    import torch
    traced=torch.jit.trace(model,dummy)
    traced.save(str(path))
    with torch.no_grad():
        a=model(dummy); b=traced(dummy); diff=float(torch.max(torch.abs(a-b)).item())
    return {'torchscript_path':str(path),'torchscript_verified':bool(diff<1e-6),'torchscript_max_abs_difference':diff}


def export_audio():
    import torch
    ck=ROOT/'models/checkpoints/goldtrace_audio_v1.pt'
    if not ck.exists(): return {'status':'checkpoint missing'}
    payload=torch.load(ck,map_location='cpu',weights_only=False); model=AudioCNN(len(payload['classes'])); model.load_state_dict(payload['state_dict']); model.eval(); dummy=torch.randn(1,1,40,97)
    edge=ROOT/'models/edge'; edge.mkdir(parents=True,exist_ok=True)
    result={'status':'partial'}; result.update(_export_torchscript(model,dummy,edge/'goldtrace_audio_v1.torchscript.pt'))
    out=edge/'goldtrace_audio_v1.onnx'
    try:
        with torch.no_grad(): torch_out=model(dummy).numpy()
        torch.onnx.export(model,dummy,out,input_names=['spectrogram'],output_names=['logits'],dynamic_axes={'spectrogram':{0:'batch',3:'time'},'logits':{0:'batch'}},opset_version=17)
        result.update({'status':'exported','onnx_path':str(out),**_verify_onnx(out,'spectrogram',dummy.numpy(),torch_out)})
    except Exception as exc:
        result['onnx_status']='unavailable'; result['onnx_reason']=str(exc)
    return result


def export_vibration():
    import torch
    ck=ROOT/'models/checkpoints/goldtrace_vibration_v1.pt'
    if not ck.exists(): return {'status':'checkpoint missing'}
    payload=torch.load(ck,map_location='cpu',weights_only=False); model=VibrationCNN(len(payload['classes'])); model.load_state_dict(payload['state_dict']); model.eval(); dummy=torch.randn(1,1,2000)
    edge=ROOT/'models/edge'; edge.mkdir(parents=True,exist_ok=True)
    result={'status':'partial'}; result.update(_export_torchscript(model,dummy,edge/'goldtrace_vibration_v1.torchscript.pt'))
    out=edge/'goldtrace_vibration_v1.onnx'
    try:
        with torch.no_grad(): torch_out=model(dummy).numpy()
        torch.onnx.export(model,dummy,out,input_names=['vibration'],output_names=['logits'],dynamic_axes={'vibration':{0:'batch',2:'time'},'logits':{0:'batch'}},opset_version=17)
        result.update({'status':'exported','onnx_path':str(out),**_verify_onnx(out,'vibration',dummy.numpy(),torch_out)})
    except Exception as exc:
        result['onnx_status']='unavailable'; result['onnx_reason']=str(exc)
    return result


def main():
    results={}
    for name,fn in (('audio',export_audio),('vibration',export_vibration)):
        try: results[name]=fn()
        except Exception as exc: results[name]={'status':'failed','reason':str(exc)}
    write_json('reports/onnx_export.json',results)
    print(json.dumps(results,indent=2))

if __name__=='__main__': main()
