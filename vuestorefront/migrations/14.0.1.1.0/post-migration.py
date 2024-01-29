def migrate(cr, version):
    cr.execute(
        """UPDATE website
        SET vsf_domain = domain
        WHERE domain IS NOT NULL
        """
    )
