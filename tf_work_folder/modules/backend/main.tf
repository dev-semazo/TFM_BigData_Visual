resource "aws_ecr_repository" "dashboard_repo" {
  name                 = "metabase_dashboard_repo"
  image_tag_mutability = "MUTABLE"
}

data "aws_ecr_lifecycle_policy_document" "lf_policy" {
  rule {
    priority    = 1
    description = "Keep Only Last Image"

    selection {
      tag_status      = "any"
      count_type      = "imageCountMoreThan"
      count_number    = 1
    }
  }
}

resource "aws_ecr_lifecycle_policy" "example" {
  repository = aws_ecr_repository.dashboard_repo.name

  policy = data.aws_ecr_lifecycle_policy_document.lf_policy.json
}
