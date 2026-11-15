# atlas-mongodb

Ansible playbooks for a three-member MongoDB replica set. Clients use the member list; there is no HAProxy.

**Playbook:** `playbooks/mongodb_cluster.yaml`  
**Catalog:** `group_vars/all/atlas-mongodb.yml`

```
          +-----------+-----------+
          |           |           |
          v           v           v
       mongo-01    mongo-02    mongo-03
       PRIMARY     SECONDARY   SECONDARY
```

| Group | Roles |
| --- | --- |
| `mongo_cluster` | `200_mongodb_node`, `201_mongodb_replicaset` |

The first sorted host is the preferred initial primary. After an election any member can become primary. Each host sets `mongodb_data_disk` to its second disk.
