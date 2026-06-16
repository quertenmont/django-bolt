from __future__ import annotations

import pytest

pytestmark = pytest.mark.server_integration


def test_runbolt_uses_default_max_param_length_without_env(make_server_project):
    project = make_server_project(
        project_api_body="""
        @api.get("/echo/{value}")
        async def echo(value: str):
            return {"length": len(value)}
        """
    )

    too_long = "a" * 8193
    with project.start() as server:
        response = server.get(f"/echo/{too_long}")

    assert response.status_code == 422
    assert "max 8192 bytes" in response.text


def test_runbolt_honors_django_bolt_max_param_length_env(make_server_project):
    project = make_server_project(
        project_api_body="""
        @api.get("/echo/{value}")
        async def echo(value: str):
            return {"length": len(value)}
        """
    )

    accepted = "a" * 10000
    rejected = "a" * 16385
    with project.start(env={"DJANGO_BOLT_MAX_PARAM_LENGTH": "16384"}) as server:
        accepted_response = server.get(f"/echo/{accepted}")
        rejected_response = server.get(f"/echo/{rejected}")

    assert accepted_response.status_code == 200
    assert accepted_response.json() == {"length": len(accepted)}
    assert rejected_response.status_code == 422
    assert "max 16384 bytes" in rejected_response.text
