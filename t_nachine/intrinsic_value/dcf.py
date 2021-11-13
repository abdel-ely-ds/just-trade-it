class DCF:
    @staticmethod
    def _compute_re(
        risk_free_rate: float, beta: float, market_risk_premium: float
    ) -> float:
        return risk_free_rate + beta * market_risk_premium

    @staticmethod
    def _compute_rd(interest_rate: float, tax_rate: float) -> float:
        return interest_rate * (1 - tax_rate)

    @staticmethod
    def _compute_mv_of_debt(bv_of_debt: float, factor: float = 1.20) -> float:
        return bv_of_debt * factor

    @staticmethod
    def compute_discount_rate(
        risk_free_rate: float,
        beta: float,
        market_risk_premium: float,
        interest_rate: float,
        tax_rate: float,
        bv_of_debt: float,
        mv_of_equity: float,
        factor: float = 1.20,
    ) -> float:
        total = (
            DCF._compute_mv_of_debt(bv_of_debt=bv_of_debt, factor=factor) + mv_of_equity
        )
        re = DCF._compute_re(
            risk_free_rate=risk_free_rate,
            beta=beta,
            market_risk_premium=market_risk_premium,
        )
        rd = DCF._compute_rd(interest_rate=interest_rate, tax_rate=tax_rate)
        mv_of_debt = DCF._compute_mv_of_debt(bv_of_debt=bv_of_debt, factor=factor)

        return re * mv_of_equity / total + rd * mv_of_debt / total

    @staticmethod
    def compute_discount_factor(discount_rate: float, n: int) -> float:
        return pow((1 + discount_rate), -n)

    @staticmethod
    def compute_projected_fcf(growth_rate: float, current_fcf: float, n: int) -> float:
        """
        projected free cash flow
        """
        return current_fcf * ((1 + growth_rate) ** n)

    @staticmethod
    def compute_discounted_dcf(
        projected_fcf: float,
        discount_factor: float,
    ) -> float:
        """
        discounted cash flow
        """
        return projected_fcf * discount_factor

    @staticmethod
    def compute_perpetuity_value(
        growth_rate: float, gdp_growth_rate: float, final_projected_fcf: float
    ) -> float:
        return (final_projected_fcf * (1 + gdp_growth_rate)) / (
            growth_rate - gdp_growth_rate
        )

    @staticmethod
    def computed_discounted_perpetuity_value(
        perpetuity_value: float, discount_factor: float
    ) -> float:
        return discount_factor * perpetuity_value

    @staticmethod
    def compute_intrinsic_value(
        cash: float,
        debt: float,
        final_discounted_perpetuity_value: float,
        shares_outstanding: float,
    ) -> float:
        value = final_discounted_perpetuity_value + cash - debt

        return value / shares_outstanding

    def __call__(
        self,
        cash,
        debt,
        shares_outstanding,
        current_fcf: float,
        growth_rate: float,
        gdb_growth_rate: float,
        interest_rate: float,
        tax_rate: float,
        mv_of_equity: float,
        bv_of_debt: float,
        beta: float,
        risk_free_rate: float,
        market_risk_premium: float,
        factor: float = 1.2,
        n: int = 10,
    ) -> float:
        discount_rate = self.compute_discount_rate(
            risk_free_rate=risk_free_rate,
            beta=beta,
            market_risk_premium=market_risk_premium,
            interest_rate=interest_rate,
            tax_rate=tax_rate,
            bv_of_debt=bv_of_debt,
            mv_of_equity=mv_of_equity,
            factor=factor,
        )

        final_projected_fcf = self.compute_projected_fcf(
            growth_rate=growth_rate, current_fcf=current_fcf, n=n
        )

        perpetuity_value = self.compute_perpetuity_value(
            growth_rate=growth_rate,
            gdp_growth_rate=gdb_growth_rate,
            final_projected_fcf=final_projected_fcf,
        )

        final_discount_factor = self.compute_discount_factor(
            discount_rate=discount_rate, n=n
        )

        final_discounted_perpetuity_value = self.computed_discounted_perpetuity_value(
            perpetuity_value=perpetuity_value, discount_factor=final_discount_factor
        )

        intrinsic_value = self.compute_intrinsic_value(
            cash=cash,
            debt=debt,
            final_discounted_perpetuity_value=final_discounted_perpetuity_value,
            shares_outstanding=shares_outstanding,
        )

        return round(intrinsic_value, 2)
