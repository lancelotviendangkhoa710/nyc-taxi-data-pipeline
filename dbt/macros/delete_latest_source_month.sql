{% macro delete_latest_source_month() %}
    {% if is_incremental() %}
        delete from {{ this }}
        where source_month >= (
            select coalesce(max(source_month), '0000-00')
            from {{ this }}
        )
    {% endif %}
{% endmacro %}