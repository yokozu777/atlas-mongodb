"""Layout tests for atlas-mongodb."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


class MongoDBLayoutTest(unittest.TestCase):
    def test_roles_and_catalog(self) -> None:
        playbook = (REPO_ROOT / "playbooks" / "mongodb_cluster.yaml").read_text(encoding="utf-8")
        for role in (
            "00_ensure_workspace",
            "01_validate_vars",
            "200_mongodb_node",
            "201_mongodb_replicaset",
        ):
            self.assertIn(role, playbook)
            self.assertTrue((REPO_ROOT / "roles" / role / "tasks" / "main.yaml").is_file(), role)
        catalog = yaml.safe_load(
            (REPO_ROOT / "group_vars" / "all" / "atlas-mongodb.yml").read_text(encoding="utf-8")
        )
        self.assertEqual(catalog["mongodb_version"], "9.0")
        self.assertEqual(catalog["mongodb_replset_name"], "atlas")
        self.assertNotIn("mongodb_admin_password", catalog)
        self.assertNotIn("mongodb_keyfile", catalog)
        secrets = yaml.safe_load(
            (REPO_ROOT / "group_vars" / "all" / "atlas-mongodb.secrets.yml").read_text(encoding="utf-8")
        )
        self.assertEqual(set(secrets), {"mongodb_admin_password", "mongodb_keyfile"})
        inventory = yaml.safe_load((REPO_ROOT / "inventory-example.yml").read_text(encoding="utf-8"))
        hosts = inventory["all"]["children"]["mongodb"]["children"]["mongo_cluster"]["hosts"]
        self.assertEqual(len(hosts), 3)
        disks = sorted(host["mongodb_data_disk"] for host in hosts.values())
        self.assertEqual(
            disks,
            [
                "/dev/disk/by-id/wwn-0x5000c500c35c5820",
                "/dev/disk/by-id/wwn-0x5000c500c35c5821",
                "/dev/disk/by-id/wwn-0x5000c500c35c5822",
            ],
        )
        initiate = (
            REPO_ROOT / "roles" / "201_mongodb_replicaset" / "templates" / "initiate.js.j2"
        ).read_text(encoding="utf-8")
        self.assertIn("priority: {{ 2 if loop.first else 1 }}", initiate)
        self.assertIn("replSetInitiate", initiate)
        self.assertNotIn("rs.status()", initiate)
        config = (
            REPO_ROOT / "roles" / "200_mongodb_node" / "templates" / "mongod.conf.j2"
        ).read_text(encoding="utf-8")
        self.assertIn("authorization: enabled", config)
        self.assertIn("replSetName:", config)
