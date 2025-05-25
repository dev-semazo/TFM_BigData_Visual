output "web_bucket_name" {
  description = "El nombre del bucket S3 de hosting web."
  value       = aws_s3_bucket.static_site.bucket
}

output "cloudfront_domain_name" {
  description = "El nombre de dominio de la distribución de CloudFront (dominio predeterminado de CloudFront)."
  value       = aws_cloudfront_distribution.s3_distribution.domain_name
}

output "cloudfront_id" {
  description = "El ID de la distribución de CloudFront."
  value       = aws_cloudfront_distribution.s3_distribution.id
}