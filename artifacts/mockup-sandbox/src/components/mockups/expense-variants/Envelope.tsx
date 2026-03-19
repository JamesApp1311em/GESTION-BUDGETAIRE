import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Save } from "lucide-react";

// The shared mock data
const initialData = {
  user: "Jean Martin",
  month: "Mars",
  year: "2026",
  income: 2500,
  expenses: {
    loyer: 650,
    scolarite: 180,
    ration: 320,
    dettes: 200,
    poche: 100,
    assistance: 150,
    autres: 80,
  }
};

const CATEGORIES = [
  { id: 'loyer', label: 'Loyer', color: 'bg-blue-500', hex: '#3b82f6' },
  { id: 'scolarite', label: 'Scolarité', color: 'bg-amber-500', hex: '#f59e0b' },
  { id: 'ration', label: 'Ration', color: 'bg-rose-500', hex: '#f43f5e' },
  { id: 'dettes', label: 'Dettes', color: 'bg-purple-500', hex: '#a855f7' },
  { id: 'poche', label: 'Poche', color: 'bg-orange-500', hex: '#f97316' },
  { id: 'assistance', label: 'Assistance', color: 'bg-teal-500', hex: '#14b8a6' },
  { id: 'autres', label: 'Autres', color: 'bg-stone-500', hex: '#78716c' },
];

export default function EnvelopeVariant() {
  const [expenses, setExpenses] = useState(initialData.expenses);
  const [isSaving, setIsSaving] = useState(false);

  const handleExpenseChange = (id: keyof typeof expenses, value: string) => {
    const numValue = value === '' ? 0 : Number(value);
    setExpenses(prev => ({ ...prev, [id]: numValue }));
  };

  const handleSave = () => {
    setIsSaving(true);
    setTimeout(() => setIsSaving(false), 1000);
  };

  const totalExpenses = Object.values(expenses).reduce((a, b) => a + (Number(b) || 0), 0);
  const savings = initialData.income - totalExpenses;
  const savingsRate = (savings / initialData.income) * 100;

  const isPositiveSavings = savings >= 0;

  return (
    <div className="min-h-screen bg-stone-50 p-4 sm:p-8 font-sans text-stone-900 flex justify-center">
      <div className="w-full max-w-3xl space-y-8">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <h2 className="text-stone-500 font-medium tracking-wide uppercase text-sm">Revenu du Mois</h2>
          <div className="text-5xl font-bold tracking-tight text-stone-800">
            ${initialData.income.toLocaleString()}
          </div>
          <p className="text-stone-500">{initialData.month} {initialData.year}</p>
        </div>

        {/* Stacked Bar Card */}
        <Card className="border-stone-200 shadow-sm overflow-hidden bg-white">
          <CardContent className="p-6 space-y-6">
            <div className="flex justify-between items-end">
              <h3 className="font-semibold text-lg text-stone-800">Allocation</h3>
              <div className={`text-right ${isPositiveSavings ? 'text-emerald-600' : 'text-red-500'}`}>
                <div className="text-sm font-medium uppercase tracking-wide">Épargne Restante</div>
                <div className="text-2xl font-bold">
                  ${savings.toLocaleString()} <span className="text-lg opacity-80">({savingsRate.toFixed(1)}%)</span>
                </div>
              </div>
            </div>

            {/* The Stacked Bar */}
            <div className="h-10 w-full flex rounded-lg overflow-hidden border border-stone-200/50 shadow-inner">
              {CATEGORIES.map(cat => {
                const amount = expenses[cat.id as keyof typeof expenses] || 0;
                const percentage = (amount / initialData.income) * 100;
                if (percentage === 0) return null;
                return (
                  <div 
                    key={cat.id} 
                    className={`${cat.color} h-full transition-all duration-300 ease-in-out`}
                    style={{ width: `${percentage}%` }}
                    title={`${cat.label}: $${amount} (${percentage.toFixed(1)}%)`}
                  />
                );
              })}
              {isPositiveSavings && (
                <div 
                  className="bg-emerald-400 h-full transition-all duration-300 ease-in-out opacity-80 striped-bg"
                  style={{ width: `${savingsRate}%` }}
                  title={`Épargne: $${savings} (${savingsRate.toFixed(1)}%)`}
                />
              )}
            </div>

            {/* Legend */}
            <div className="flex flex-wrap gap-x-6 gap-y-3 text-sm text-stone-600 pt-4">
              {CATEGORIES.map(cat => {
                const amount = expenses[cat.id as keyof typeof expenses] || 0;
                const percentage = (amount / initialData.income) * 100;
                return (
                  <div key={cat.id} className="flex items-center gap-1.5">
                    <div className={`w-3 h-3 rounded-full ${cat.color}`} />
                    <span className="font-medium">{cat.label}</span>
                    <span className="text-stone-800 font-semibold">${amount}</span>
                    <span className="text-stone-400">({percentage.toFixed(1)}%)</span>
                  </div>
                );
              })}
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full bg-emerald-400" />
                <span className="font-medium text-emerald-700">Épargne</span>
                <span className="text-stone-800 font-semibold">${savings}</span>
                <span className="text-stone-400">({isPositiveSavings ? savingsRate.toFixed(1) : 0}%)</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Envelope Inputs List */}
        <Card className="border-stone-200 shadow-sm bg-white">
          <CardHeader className="pb-4">
            <CardTitle className="text-xl">Enveloppes de Dépenses</CardTitle>
            <CardDescription>Ajustez les montants alloués à chaque catégorie.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {CATEGORIES.map(cat => {
              const amount = expenses[cat.id as keyof typeof expenses] || 0;
              const percentage = (amount / initialData.income) * 100;
              return (
                <div key={cat.id} className="group">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className={`w-4 h-4 rounded-full ${cat.color} shadow-sm`} />
                      <Label htmlFor={cat.id} className="text-base font-medium cursor-pointer">
                        {cat.label}
                      </Label>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-stone-400 font-medium w-12 text-right text-sm">
                        {percentage.toFixed(1)}%
                      </span>
                      <div className="relative w-32">
                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-stone-500">$</span>
                        <Input 
                          id={cat.id}
                          type="number" 
                          value={amount.toString()} 
                          onChange={(e) => handleExpenseChange(cat.id as keyof typeof expenses, e.target.value)}
                          className="pl-7 bg-stone-50/50 border-stone-200 focus-visible:ring-stone-400"
                        />
                      </div>
                    </div>
                  </div>
                  <div className="w-full bg-stone-100 rounded-full h-1.5 overflow-hidden ml-7" style={{ width: 'calc(100% - 28px)' }}>
                    <div 
                      className={`h-1.5 rounded-full ${cat.color} transition-all duration-300`} 
                      style={{ width: `${Math.min(percentage, 100)}%` }}
                    />
                  </div>
                </div>
              );
            })}

            <Separator className="my-6" />

            {/* Savings Row */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <div className="w-4 h-4 rounded-full bg-emerald-500 shadow-sm" />
                  <Label className="text-base font-bold text-emerald-700">
                    Épargne
                  </Label>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`font-medium w-12 text-right text-sm ${isPositiveSavings ? 'text-emerald-600' : 'text-red-500'}`}>
                    {savingsRate.toFixed(1)}%
                  </span>
                  <div className="relative w-32">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-emerald-600">$</span>
                    <Input 
                      readOnly
                      value={savings.toString()} 
                      className={`pl-7 font-bold border-transparent bg-emerald-50 ${isPositiveSavings ? 'text-emerald-700' : 'text-red-600 bg-red-50'}`}
                    />
                  </div>
                </div>
              </div>
              <div className="w-full bg-stone-100 rounded-full h-1.5 overflow-hidden ml-7" style={{ width: 'calc(100% - 28px)' }}>
                <div 
                  className={`h-1.5 rounded-full ${isPositiveSavings ? 'bg-emerald-500' : 'bg-red-500'} transition-all duration-300`} 
                  style={{ width: `${Math.min(Math.max(savingsRate, 0), 100)}%` }}
                />
              </div>
            </div>

          </CardContent>
          <CardFooter className="pt-2 pb-6 px-6">
            <Button 
              onClick={handleSave} 
              disabled={isSaving}
              className="w-full py-6 text-lg bg-stone-800 hover:bg-stone-900 text-white shadow-md transition-all active:scale-[0.98]"
            >
              {isSaving ? (
                <span className="flex items-center gap-2">
                  <span className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Sauvegarde...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <Save className="w-5 h-5" />
                  Calculer & Sauvegarder
                </span>
              )}
            </Button>
          </CardFooter>
        </Card>

      </div>
      
      {/* Add a subtle striped background pattern for savings bar */}
      <style dangerouslySetInnerHTML={{__html: `
        .striped-bg {
          background-image: linear-gradient(45deg, rgba(255, 255, 255, 0.15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, 0.15) 50%, rgba(255, 255, 255, 0.15) 75%, transparent 75%, transparent);
          background-size: 1rem 1rem;
        }
      `}} />
    </div>
  );
}
