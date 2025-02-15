#设计 HDF5 结构化存储体系
class ExperienceReplay:
    def log_episode(self, 
                  observation: PointCloud, 
                  action_sequence: List[str],
                  success_flag: bool):
        # 存储时空特征图与动作轨迹的关联
        self.memory.append({
            'obs_hash': hash(observation),
            'action_graph': nx.to_dict_of_dicts(action_graph),
            'reward': self.calculate_sparse_reward(success_flag)
        })

#引入基于注意力机制的检索模块，实现相似场景的快速匹配

