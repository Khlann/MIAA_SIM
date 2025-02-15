class Causal_Analyzer:
    def __init__ (self):
        pass
    
    classification_decision_tree = """
    A[感知失败] --> B{存在检测置信度>0.7?}
    B -->|是| C[检查局部遮挡]
    B -->|否| D[启动场景重建]
    C --> E{存在部分特征匹配?}
    E -->|是| F[标记为部分遮挡]
    E -->|否| G[判定为视野外]
    """