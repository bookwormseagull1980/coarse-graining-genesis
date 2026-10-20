# -*- coding: utf-8 -*-
"""Second-order interval jets for validated one-dimensional quadrature.

A jet carries a value, first derivative and second derivative over an
interval.  The operations below are the standard interval extensions; they
let a smooth integrand provide an outward bound on its second derivative,
which is the remainder used by the composite trapezoid rule.
"""

from __future__ import annotations

from dataclasses import dataclass

from cg_core.rational_interval import Interval, exp_negative, log_positive


@dataclass(frozen=True)
class Jet2:
    v: Interval
    d1: Interval
    d2: Interval

    @staticmethod
    def point(value: Interval) -> "Jet2":
        return Jet2(value, Interval.point(0), Interval.point(0))

    @staticmethod
    def variable(value: Interval) -> "Jet2":
        return Jet2(value, Interval.point(1), Interval.point(0))

    def __add__(self, other: "Jet2") -> "Jet2":
        return Jet2(self.v + other.v, self.d1 + other.d1, self.d2 + other.d2)

    def __sub__(self, other: "Jet2") -> "Jet2":
        return Jet2(self.v - other.v, self.d1 - other.d1, self.d2 - other.d2)

    def __neg__(self) -> "Jet2":
        return Jet2(-self.v, -self.d1, -self.d2)

    def __mul__(self, other: "Jet2") -> "Jet2":
        return Jet2(
            self.v * other.v,
            self.d1 * other.v + self.v * other.d1,
            self.d2 * other.v + 2 * self.d1 * other.d1 + self.v * other.d2,
        )

    def reciprocal(self) -> "Jet2":
        inv = 1 / self.v
        return Jet2(
            inv,
            -self.d1 / (self.v ** 2),
            2 * (self.d1 ** 2) / (self.v ** 3) - self.d2 / (self.v ** 2),
        )

    def __truediv__(self, other: "Jet2") -> "Jet2":
        return self * other.reciprocal()

    def exp_negative(self) -> "Jet2":
        """exp(-v) for a nonnegative interval v."""
        value = exp_negative(self.v)
        return Jet2(value, -value * self.d1, value * (self.d1 ** 2 - self.d2))

    def sqrt(self) -> "Jet2":
        value = self.v.sqrt()
        return Jet2(
            value,
            self.d1 / (2 * value),
            self.d2 / (2 * value) - (self.d1 ** 2) / (4 * (value ** 3)),
        )

    def log(self) -> "Jet2":
        return Jet2(
            log_positive(self.v),
            self.d1 / self.v,
            self.d2 / self.v - (self.d1 ** 2) / (self.v ** 2),
        )

    def pow_int(self, n: int) -> "Jet2":
        if n == 0:
            return Jet2.point(Interval.point(1))
        if n < 0:
            return (self ** (-n)).reciprocal()
        result = Jet2.point(Interval.point(1))
        base = self
        k = n
        while k:
            if k & 1:
                result = result * base
            base = base * base
            k >>= 1
        return result

    def __pow__(self, n: int) -> "Jet2":
        if not isinstance(n, int):
            raise TypeError("Jet2 powers are integer powers")
        return self.pow_int(n)


def jet_value(interval: Interval) -> Jet2:
    return Jet2.variable(interval)
