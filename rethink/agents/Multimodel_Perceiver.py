class Multimodel_Perceiver:
    def __init__(self) -> None:
        pass
    
    output_example = {
        "graspability": {
            "visibility_score": 0-1,
            "clearance_distance": float,
            "occlusion_status": ["none", "partial", "full"]
        },
        "candidate_objects": [
            {
            "mask": binary_matrix,
            "confidence": 0.85,
            "spatial_info": {"x": 0.3, "y": 0.5, "z": 0.2}
            }
        ]
    }
        